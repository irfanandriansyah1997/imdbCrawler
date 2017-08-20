# -*- coding: utf-8 -*-
import re
import scrapy
import unicodedata

from datetime import datetime
from imdbCrawler.items import ActressDetail
from imdbCrawler.library.general_function import convert_date
from imdbCrawler.library.mongo_pipeline import MongoPipeline
from imdbCrawler.library.required_fields_pipeline import RequiredFieldsPipeline

class ActressDetailSpider(scrapy.Spider):
    name = "actress-bio"
    allowed_domains = []
    base_url = None
    start_urls = []
    collection = None
    pipeline = set([MongoPipeline, RequiredFieldsPipeline])
    required_fields = ["actress_id", "actress_height", "actress_birth", "actress_nickname", "actress_bio"]
    mongo_requirement = {
        "primary": "actress_id",
        "collection": "actress",
        "source": "bio"
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

        self.start_urls = ['http://www.imdb.com/name/nm3592338/bio', 'http://www.imdb.com/name/nm1099909/bio', 'http://www.imdb.com/name/nm7959394']

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

    def parse(self, response):
        birth = dict()
        birth.update({'date': {}})
        birth.update({'place': None})

        birth_date = response.css("#overviewTable > tr:nth-child(1) > td:nth-child(2) > time::attr(datetime)")
        if birth_date:
            birth_date = birth_date.extract_first().strip()
            birth.update({"date": convert_date(birth_date, "%Y-%m-%d")})
        else:
            birth.update({"date": convert_date('', "%Y-%m-%d")})

        print '*****************************************************************'
        print birth
        # print response.css("#overviewTable > tr.even > td:nth-child(2) > a::text").extract_first().strip()
        print '*****************************************************************'

