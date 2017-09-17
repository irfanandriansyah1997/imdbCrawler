# -*- coding: utf-8 -*-
import re
import scrapy
import unicodedata

from imdbCrawler.items import FilmList
from imdbCrawler.library.mongo_pipeline import MongoPipeline
from imdbCrawler.library.general_function import convert_photo
from imdbCrawler.library.required_fields_pipeline import RequiredFieldsPipeline

class FilmListSpider(scrapy.Spider):
    name = "film-list"
    allowed_domains = []
    base_url = None
    start_urls = []
    collection = None
    pipeline = set([
        MongoPipeline,
        RequiredFieldsPipeline,

    ])
    required_fields = ["film_id", "film_title", "film_title"]
    mongo_requirement = {
        "primary": "film_id",
        "collection": "film",
        "source": "list"
    }

    def __init__(self, data):
        scrapy.Spider.__init__(self)
        self.per_page = 50

        self.base_url = data.get("base_url")
        self.collection = data.get("collection").get("film")
        self.allowed_domains = [x for x in data.get("allowed_domains")]

        # self.start_urls = self.populate_start_urls(data.get("start_url").get("film-list")[0], 201)
        self.start_urls = self.populate_start_urls("http://www.imdb.com/search/title?release_date=2017&page=0", 3)

    def populate_start_urls(self, url, range_loop):
        return [url.replace("page=0", "page={}".format(index)) for index in range(0, range_loop)]

    @classmethod
    def from_crawler(cls, crawler):
        data = dict()
        data.update({"base_url": crawler.settings.get("BASE_URL")})
        data.update({"start_url": crawler.settings.get("START_URL")})
        data.update({"collection": crawler.settings.get("COLLECTION")})
        data.update({"allowed_domains": crawler.settings.get("ALLOWED_DOMAIN")})
        return cls(data)

    def parse(self, response):
        list_film = response.css("#main > div > div > div.lister-list > div.lister-item")

        for item in list_film:
            title = item.css(".lister-item-content > .lister-item-header > a::text").extract_first()
            title = title.strip() if title else None

            temp_year = item.css(".lister-item-content > .lister-item-header > .lister-item-year::text").extract_first()
            temp_year = re.sub("[()]", "",temp_year).replace(u"\u2013","5432112345") if temp_year else ""
            temp_year = re.sub("[^0-9.]+", "", temp_year).split("5432112345")

            if len(temp_year) > 1:
                temp_year[1] = int(temp_year[1]) if temp_year[1] != '' else 'On Going'

            if len(temp_year) > 0:
                year = {'start': int(temp_year[0]), 'end': temp_year[1] } if len(temp_year) > 1\
                        else {'start': int(temp_year[0]), 'end': int(temp_year[0])}
            else:
                year = {'start': 'Info Not Found', 'end': 'Info Not Found'}

            length = item.css(".lister-item-content > p > span.runtime::text").extract_first()
            length = int(re.sub("[^0-9.]+", "", length.strip())) if length else 'Data not found'

            genre = item.css(".lister-item-content > p > span.genre::text").extract_first()
            genre = [x.strip() for x in (genre.strip().split(',') if genre else [])]

            short_description = item.css(".lister-item-content > p:nth-child(4)::text").extract_first()
            short_description = short_description.strip() if short_description else "Short description is not found"
            short_description = short_description.split("...")[0]

            rating = dict()
            imdb_rating = item.css(".lister-item-content > .ratings-bar > .ratings-imdb-rating::attr(data-value)")\
                .extract_first()
            imdb_rating = float(re.sub("[^0-9.]+", "", imdb_rating.strip()).replace(",", ".")) if imdb_rating else \
                "IMDB rating is not found"

            meta_score = item.css(".lister-item-content > .ratings-bar > .ratings-metascore > span.metascore::text")\
                .extract_first()

            meta_score = int(re.sub("[^0-9.]+", "", meta_score.strip())) if meta_score \
                else "Metascore rating is not found"

            rating.update({"imdb": imdb_rating, "metascore": meta_score})

            button = item.css(".lister-item-content > .lister-item-header > a::attr(href)").extract_first().strip()

            image = convert_photo(item.css(".lister-item-image > a > img::attr(loadlate)").extract_first().strip(), "film-list")

            item = FilmList()
            item.update({"film_id": re.sub(r"title.+?", "", button).split("/")[1]})
            item.update({"film_year": year})
            item.update({"film_title": title})
            item.update({"film_genre": genre})
            item.update({"film_photo": image})
            item.update({"film_length": length})
            item.update({"film_rating": rating})
            item.update({"film_description_short": unicodedata.normalize('NFKD', short_description).encode('ascii','ignore')})

            yield item
