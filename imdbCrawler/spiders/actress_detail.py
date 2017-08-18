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
    start_urls = ["http://www.imdb.com/name/nm3592338/"]
    collection = None
    pipeline = set([])
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

        print self.start_urls

    @classmethod
    def from_crawler(cls, crawler):
        data = dict()
        data.update({"base_url": crawler.settings.get("BASE_URL")})
        data.update({"collection": crawler.settings.get("COLLECTION")})
        data.update({"allowed_domains": crawler.settings.get("ALLOWED_DOMAIN")})
        return cls(data)

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
        tempYear = component.css("span.year_column::text").extract_first().strip().split('-')

        year = {'start': int(tempYear[0]), 'end': int(tempYear[1])} \
            if len(tempYear) > 1 \
            else {'start': int(tempYear[0]), 'end': int(tempYear[0])}

        film = component.css("b > a::text").extract_first().strip()

        return {'year' : year, 'film' : film}


