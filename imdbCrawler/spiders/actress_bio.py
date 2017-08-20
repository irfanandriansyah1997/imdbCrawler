# -*- coding: utf-8 -*-
import re
import scrapy
import unicodedata

from datetime import datetime
from imdbCrawler.items import ActressBio
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
    required_fields = ["actress_id", "actress_height", "actress_birth", "actress_bio"]
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

        self.start_urls = self.populate_start_urls()

    def populate_start_urls(self):
        BASE_URL = "http://www.imdb.com/name/"
        db = self.db.get(
            "actress",
            where={
                "actress_birth": {"$exists": False},
                "actress_bio": {"$exists": False}
            }
        )

        return ['{}{}/bio'.format(BASE_URL, a.get('actress_id')) for a in db.get('data')]

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
        height = None

        birth_date = response.css("#overviewTable > tr:nth-child(1) > td:nth-child(2) > time::attr(datetime)")\
            .extract_first()
        if birth_date:
            birth_date = birth_date.strip()
            birth.update({"date": convert_date(birth_date, "%Y-%m-%d")})
        else:
            birth.update({"date": convert_date('', "%Y-%m-%d")})

        place = response.css("#overviewTable > tr.even > td:nth-child(2) > a::text").extract_first()
        if place:
            place = place.strip()
            birth.update({"place": str(unicodedata.normalize('NFKD', place).encode('ascii','ignore'))})
        else:
            birth.update({"place": "Oops data not found"})

        field_key = [str(i).lower()for i in response.css("#overviewTable > tr > td.label::text").extract()]
        field_value = [unicodedata.normalize('NFKD', self.strip_html(i).strip()).encode('ascii','ignore')
                       if i else '-'
                       for i in response.css("#overviewTable > tr > td:last-child").extract()]

        key = dict(zip(field_key, field_value))
        if 'born' in key: del key['born']
        if 'height' in key:
            height = key.get('height').strip()
            del key['height']

        bio_element = response.css("#bio_content > div.soda")
        bio = ''.join([self.strip_html(a.strip()) for a in bio_element[0].css('p').extract()])

        url = self.replaceText(response.url.replace(self.base_url, ''), '?')

        item = ActressBio()
        item.update({"actress_id": re.sub(r"name.+?", "", url).strip("/")})
        item.update({"actress_height": height})
        item.update({"actress_birth": birth})
        item.update({"actress_personal_detail": key})
        item.update({"actress_bio": bio})
        
        yield item


    def strip_html(self, data):
        data = "\line".join(data.split("<br>"))
        p = re.compile(r'<.*?>')
        data = p.sub('', data)
        data = re.sub("\n + ? +", "", data)
        return "\n".join(data.split("\line"))

    def replaceText(self, text, keyword):
        there = re.compile(re.escape('{}'.format(keyword)) + '.*')
        return there.sub('', text)[1:].replace('/bio','')

