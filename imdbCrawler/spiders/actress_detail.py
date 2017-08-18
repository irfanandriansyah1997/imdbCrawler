# -*- coding: utf-8 -*-
import re
import scrapy
import unicodedata

from imdbCrawler.items import ActressDetail
from imdbCrawler.library.mongo_pipeline import MongoPipeline
from imdbCrawler.library.required_fields_pipeline import RequiredFieldsPipeline

class ActressDetailSpider(scrapy.Spider):
    name = "actress-detail"
    allowed_domains = []
    base_url = None
    start_urls = []
    collection = None
    pipeline = set([MongoPipeline, RequiredFieldsPipeline])
    required_fields = ["actress_name", "actress_category", "actress_filmography", "actress_height"]
    mongo_requirement = {
        "primary": "actress_id",
        "collection": "actress",
        "source": "detail"
    }

    def __init__(self, data):
        scrapy.Spider.__init__(self)
        self.base_url = data.get("base_url")
        self.collection = data.get("collection").get("actress")
        self.allowed_domains = [x for x in data.get("allowed_domains")]
        self.db = MongoPipeline(
                    data.get("database").get("host"),
                    data.get("database").get("port"),
                    data.get("database").get("db")
                )

        self.start_urls = self.populate_start_urls()

    @classmethod
    def from_crawler(cls, crawler):
        data = dict()
        data.update({"base_url": crawler.settings.get("BASE_URL")})
        data.update({"collection": crawler.settings.get("COLLECTION")})
        data.update({"allowed_domains": crawler.settings.get("ALLOWED_DOMAIN")})
        data.update({"database" : {
            "host" : crawler.settings.get("MONGODB_HOST"),
            "port" : crawler.settings.get("MONGODB_PORT"),
            "db" : crawler.settings.get("MONGODB_DB")
        }})
        return cls(data)

    def populate_start_urls(self):
        BASE_URL = "http://www.imdb.com/name/"
        db = self.db.get(
                "actress",
                where={
                    "actress_category" : {"$exists" : False},
                    "actress_filmography" : {"$exists" : False}
                }
        )

        return ['{}{}'.format(BASE_URL, a.get('actress_id')) for a in db.get('data')]

    def parse(self, response):
        name = response.css("#overview-top > h1 > span.itemprop::text").extract_first().strip()
        category = [
            str(item.css('span::text').extract_first().strip().lower())
            for item in response.css("#name-job-categories > a")
        ]

        film_component = response.css("#filmography > div > div.filmo-row")
        filmography = [self.parsingFilm(item) for item in film_component]
        height = response.css("#details-height::text").extract()

        height = unicodedata.normalize('NFKD', height[1].strip()).encode('ascii','ignore') if height else '-'

        url = self.replaceText(response.url.replace(self.base_url, ''), '?')

        item = ActressDetail()
        item.update({"actress_id": re.sub(r"name.+?", "", url).strip("/")})
        item.update({"actress_name": name})
        item.update({"actress_category": category})
        item.update({"actress_filmography": filmography})
        item.update({"actress_height": height})

        yield item

    def replaceText(self, text, keyword):
        there = re.compile(re.escape('{}'.format(keyword)) + '.*')
        return there.sub('', text)

    def parsingFilm(self, component):
        tempYear = filter(None, component.css("span.year_column::text").extract_first().strip().split('-'))

        if len(tempYear) > 0:
            year = {'start': int(re.sub('[^0-9.]+', '', tempYear[0])), 'end': int(re.sub('[^0-9.]+', '', tempYear[1]))} \
                if len(tempYear) > 1 \
                else {'start': int(re.sub('[^0-9.]+', '', tempYear[0])), 'end': int(re.sub('[^0-9.]+', '', tempYear[0]))}
        else:
            year = {'start': 'Info Not Found', 'end': 'Info Not Found'}

        film = component.css("b > a::text").extract_first().strip()

        return {'year' : year, 'film' : film}


