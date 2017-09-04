# -*- coding: utf-8 -*-
import re
import scrapy
import unicodedata

from imdbCrawler.items import FilmPhoto
from imdbCrawler.library.general_function import convert_photo
from imdbCrawler.library.mongo_pipeline import MongoPipeline
from imdbCrawler.library.required_fields_pipeline import RequiredFieldsPipeline

class FilmSynopsisSpider(scrapy.Spider):
    name = "film-media"
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
        "source": "media"
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
                "film_media": {"$exists": False}
            }
            # ,
            # limit=100
        )

        return ['{}{}/mediaindex'.format(BASE_URL, a.get('film_id')) for a in db.get('data')]

    def parse(self, response):
        tag = response.css("#media_index_thumbnail_grid > a > img::attr(src)").extract()
        media = [convert_photo(index, "media") for index in tag]
        url = self.replaceText(response.url.replace(self.base_url, ''), '?')

        item = FilmPhoto()
        item.update({"film_id": re.sub(r"title.+?", "", url).strip("/")})
        item.update({"film_media": media if type(media) is list else []})
        yield item

    def replaceText(self, text, keyword):
        there = re.compile(re.escape('{}'.format(keyword)) + '.*')
        return there.sub('', text)[1:].replace('/mediaindex','')