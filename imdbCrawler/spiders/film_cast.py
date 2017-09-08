# -*- coding: utf-8 -*-
import re
import scrapy

from datetime import datetime

import unicodedata

from imdbCrawler.items import FilmCrew
from imdbCrawler.library.mongo_pipeline import MongoPipeline
from imdbCrawler.library.general_function import convert_photo, tic, toc
from imdbCrawler.library.required_fields_pipeline import RequiredFieldsPipeline

class FilmDetailSpider(scrapy.Spider):
    name = "film-crew"
    allowed_domains = []
    base_url = None
    start_urls = []
    collection = None
    pipeline = set([
        MongoPipeline,
        RequiredFieldsPipeline
    ])
    required_fields = ["film_id"]
    mongo_requirement = {
        "primary": "film_id",
        "collection": "film",
        "source": "crew"
    }

    def __init__(self, data):
        scrapy.Spider.__init__(self)
        self.base_url = data.get("base_url")
        self.collection = data.get("collection").get("film")
        self.allowed_domains = [x for x in data.get("allowed_domains")]
        self.db = MongoPipeline(
            data.get("database").get("host"),
            data.get("database").get("port"),
            data.get("database").get("db")
        )
        self.start_urls = self.populate_start_urls()
        # self.start_urls = ["http://www.imdb.com/title/tt3315342/fullcredits"]

    @classmethod
    def from_crawler(cls, crawler):
        data = dict()
        data.update({"base_url": crawler.settings.get("BASE_URL")})
        data.update({"collection": crawler.settings.get("COLLECTION")})
        data.update({"allowed_domains": crawler.settings.get("ALLOWED_DOMAIN")})
        data.update({"database": {
            "host": crawler.settings.get("MONGODB_HOST"),
            "port": crawler.settings.get("MONGODB_PORT"),
            "db": crawler.settings.get("MONGODB_DB")
        }})
        return cls(data)

    def populate_start_urls(self):
        BASE_URL = "http://www.imdb.com/title/"
        db = self.db.get(
            "film",
            where={
                # "film_crew": {"$exists": False},
                # "film_cast": {"$exists": False}
            }
        )

        return ['{}{}/fullcredits'.format(BASE_URL, a.get('film_id')) for a in db.get('data')]

    def parse(self, response):
        reprocess = dict()
        reprocess.update({"data": []})

        heading = response.css("#fullcredits_content > h4::text").extract()
        table = response.css("#fullcredits_content > table")
        tic()
        heading = [i.strip() if i.strip() != '' else None for i in heading]
        heading = filter(lambda x: x is not None and x != 'Cast', heading)

        table_data = list()
        for item in table:
            temporary = list()
            name = item.css("tr > td.name > a::text").extract()
            link = item.css("tr > td.name > a::attr(href)").extract()
            credit = item.css("tr > td.credit::text").extract()

            for item in link:
                reprocess["data"].append(re.sub(r"name.+?", "", item.strip()).split("?")[0].strip("/"))

            temporary = [{
                        "name": unicodedata.normalize('NFKD', x.strip()).encode('ascii', 'ignore'),
                        "actress_id" : re.sub(r"name.+?", "", link[k].strip()).split("?")[0].strip("/"),
                        "credit": unicodedata.normalize('NFKD', credit[k].strip()).encode('ascii', 'ignore')
                        if len(credit) > k is not None else None
                    }
                    for k, x  in enumerate(name)]

            if len(temporary) > 0:
                table_data.append(temporary)

        data = dict(zip(heading, table_data))

        # Cast
        list_cast = list()
        cast_table = response.css("#fullcredits_content > table.cast_list > tr")
        for item in cast_table:
            temporary = dict()
            name = item.css("td.itemprop > a > span::text").extract_first()
            link = item.css("td.itemprop > a::attr(href)").extract_first()
            credit = ""
            credit_div = item.css("td.character > div::text").extract()
            credit_div = ''.join([re.sub("\s\s+", " ", x).lstrip(" ") for x in credit_div])
            credit_link = item.css("td.character > div > a::text").extract_first()
            if credit_link:
                credit = credit_link.strip()
                credit = unicodedata.normalize('NFKD', credit).encode('ascii', 'ignore')

            if credit_div:
                credit_div = re.sub("\s\s+", " ", credit_div).lstrip(" ")
                credit_div = unicodedata.normalize('NFKD', credit_div).encode('ascii', 'ignore')
                credit = "{} {}".format(credit, credit_div)

            if name is not None and link is not None:
                temporary.update({"name": unicodedata.normalize('NFKD', name.strip()).encode('ascii', 'ignore')})
                temporary.update({"credit": credit.lstrip(" ")})
                temporary.update({"actress_id": re.sub(r"name.+?", "", link.strip()).split("?")[0].strip("/")})

                reprocess["data"].append(temporary.get("actress_id"))

                list_cast.append(temporary)

        toc(save=True, fmt=True)
        url = self.replaceText(response.url.replace(self.base_url, ''), '?')

        reprocess.update({"id": re.sub(r"title.+?", "", url).strip("/")})
        reprocess.update({"status": "checked"})
        self.reprocessActress(reprocess, reprocess.get("id"))

        item = FilmCrew()
        item.update({"film_id": re.sub(r"title.+?", "", url).strip("/")})
        item.update({"film_crew": data})
        item.update({"film_cast": list_cast})

        yield item

    def replaceText(self, text, keyword):
        there = re.compile(re.escape('{}'.format(keyword)) + '.*')
        return there.sub('', text)[1:].replace('/fullcredits', '')

    def reprocessActress(self, data, id):
        collection = "reprocess_item_actress"
        
        result = self.db.get(collection, where={"id": id})

        if result.get("count") == 0:
            self.db.insertOne(collection, data, id)
        else:
            self.db.updateOne(collection, data, {'key': "id", 'value': str(id)})
