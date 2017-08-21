# -*- coding: utf-8 -*-
import re
import scrapy
import unicodedata

from imdbCrawler.items import ActressPhoto
from imdbCrawler.library.general_function import convert_photo
from imdbCrawler.library.mongo_pipeline import MongoPipeline
from imdbCrawler.library.required_fields_pipeline import RequiredFieldsPipeline

class ActressDetailSpider(scrapy.Spider):
    name = "actress-media"
    allowed_domains = []
    base_url = None
    start_urls = []
    collection = None
    pipeline = set([MongoPipeline, RequiredFieldsPipeline])
    required_fields = ["actress_id", "actress_media"]
    mongo_requirement = {
        "primary": "actress_id",
        "collection": "actress",
        "source": "media"
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
                "actress_media": {"$exists": False}
            }
        )

        return ['{}{}/mediaindex'.format(BASE_URL, a.get('actress_id')) for a in db.get('data')]

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
        tag = response.css("#media_index_thumbnail_grid > a > img::attr(src)").extract()
        media = [convert_photo(index, "media") for index in tag]
        url = self.replaceText(response.url.replace(self.base_url, ''), '?')

        item = ActressPhoto()
        item.update({"actress_id": re.sub(r"name.+?", "", url).strip("/")})
        item.update({"actress_media": media if media is not list else []})

        yield item


    def strip_html(self, data):
        data = "\line".join(data.split("<br>"))
        p = re.compile(r'<.*?>')
        data = p.sub('', data)
        data = re.sub("\n + ? +", "", data)
        return "\n".join(data.split("\line"))

    def replaceText(self, text, keyword):
        there = re.compile(re.escape('{}'.format(keyword)) + '.*')
        return there.sub('', text)[1:].replace('/mediaindex','')

