# -*- coding: utf-8 -*-
import re
import scrapy
import unicodedata

from imdbCrawler.items import FilmSynopsis
from imdbCrawler.library.mongo_pipeline import MongoPipeline
from imdbCrawler.library.required_fields_pipeline import RequiredFieldsPipeline

class FilmSynopsisSpider(scrapy.Spider):
    name = "film-synopsis"
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
        "source": "synopsis"
    }

    def __init__(self, data):
        scrapy.Spider.__init__(self)
        self.base_url = data.get("base_url")
        self.collect = data.get("collection").get("film")
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
                "film_synopsis": {"$exists": False}
            },
            limit=78
        )

        return ['{}{}/synopsis'.format(BASE_URL, a.get('film_id')) for a in db.get('data')]

    def parse(self, response):
        synopsis = response.css("#swiki_body > div:nth-child(2) > .display > div[id*='swiki'] > div::text").extract()
        synopsis = [
            str(unicodedata.normalize('NFKD', x.strip()).encode('ascii', 'ignore')) if x
            else "Synopsis is not found"
            for x in synopsis
        ]

        synopsis = "Synopsis is not found" if len(synopsis) == 1 and synopsis[0] == "" else "\n".join(synopsis)
        url = self.replaceText(response.url.replace(self.base_url, ''), '?')

        item = FilmSynopsis()
        item.update({"film_id": re.sub(r"title.+?", "", url).strip("/")})
        item.update({"film_synopsis": synopsis})

        yield item

    def replaceText(self, text, keyword):
        there = re.compile(re.escape('{}'.format(keyword)) + '.*')
        return there.sub('', text)[1:].replace('/synopsis','')