# -*- coding: utf-8 -*-
import re
import scrapy

from datetime import datetime

import unicodedata

from imdbCrawler.items import FilmDetail
from imdbCrawler.library.mongo_pipeline import MongoPipeline
from imdbCrawler.library.general_function import convert_photo
from imdbCrawler.library.required_fields_pipeline import RequiredFieldsPipeline

class FilmDetailSpider(scrapy.Spider):
    name = "film-detail"
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
        "source": "list"
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
                "film_stars": {"$exists": False}
            },
            limit=20
        )

        return ['{}{}'.format(BASE_URL, a.get('film_id')) for a in db.get('data')]

    def parse(self, response):
        name = response.css(".titleBar > .title_wrapper > h1::text").extract_first()
        if name:
            name = name.strip()

        temp_year = response.css("#titleYear > a::text").extract_first()
        temp_year = re.sub("[()]", "", temp_year)\
            .replace(u"\u2013", "5432112345").replace(u"-", "5432112345") if temp_year else ""
        temp_year = re.sub("[^0-9.]+", "", temp_year).split("5432112345")

        if len(temp_year) > 1:
            temp_year[1] = int(temp_year[1]) if temp_year[1] != '' else 'On Going'

        if len(temp_year) > 0 and temp_year[0] != "":
            year = {'start': int(temp_year[0]), 'end': temp_year[1]} if len(temp_year) > 1 \
                else {'start': int(temp_year[0]), 'end': int(temp_year[0])}
            type = "Movie"
        else:
            component = response.css(".titleBar > .title_wrapper > .subtext > a[href*='title']::text").extract_first()
            year = self.get_year_movie(component)
            type = "TV Series"

        length = response.css(".titleBar > .title_wrapper > .subtext > time[itemprop='duration']::attr(datetime)").extract_first()
        length = int(re.sub("[^0-9.]+", "", length.strip())) if length else 'Data not found'

        short_description = response.css(".plot_summary_wrapper > .plot_summary > .summary_text::text").extract_first()
        if short_description:
            short_description = short_description.strip()

        person_title = response.css("div.plot_summary > .credit_summary_item > h4::text") \
            .extract()
        person_title = [re.sub("[^a-zA-Z]+", "", item).lower() if item else None for item in person_title]

        person_value_html = response.css("div.plot_summary > .credit_summary_item")
        person_value = list()
        for item in person_value_html:
            user = item.css("span > a > span::text").extract()
            user = [{"name": str(
                unicodedata.normalize('NFKD', x.strip()).encode('ascii', 'ignore')
            )} if x else {"name": None} for x in user]

            link = item.css("span > a::attr(href)").extract()
            link = [{"id": str(x.strip().split("?")[0].replace("/name/", ""))} if {"id": None} else None for x in link]

            [x.update(link[i]) for i, x in enumerate(user)]

            person_value.append(user)

        person = dict(zip(person_title, person_value))

        rating = dict()
        imdbRating = response.css("div.imdbRating > div.ratingValue > strong > span::text").extract_first()
        if imdbRating:
            imdbRating = float(imdbRating.strip().replace(",","."))
        else:
            imdbRating = "IMDB rating is not found"

        metascoreRating = response.css("div.titleReviewBar > .titleReviewBarItem > a > div.metacriticScore > span::text").extract_first()
        if metascoreRating:
            metascoreRating = int(metascoreRating.strip().replace(",", "."))
        else:
            metascoreRating = "Metascore rating is not found"

        rating.update({"imdb": imdbRating, "metascore": metascoreRating})

        genreElement = response.css(".titleBar > .title_wrapper > .subtext > a[href*='genre']")
        genre = list()
        for item in genreElement:
            genreItems = item.css("span::text").extract_first()
            if genreItems:
                genre.append(str(genreItems.strip()))

        time = dict()
        date_release = response.css(".titleBar > .title_wrapper > .subtext > a[href*='title'] > meta::attr(content)").extract_first()
        if date_release:
            time.update({"iso": datetime.strptime(date_release.strip(), '%Y-%M-%d')})
            time.update({"year": time.get("iso").strftime("%Y")})
            time.update({"month": time.get("iso").strftime("%m")})
            time.update({"date": time.get("iso").strftime("%d")})
        else:
            time.update({"iso": None})
            time.update({"year": None})
            time.update({"month": None})
            time.update({"date": None})

        contentRating = response.css(".titleBar > .title_wrapper > .subtext > meta[itemprop='contentRating']::attr(content)").extract_first()
        if contentRating:
            contentRating = contentRating.strip()

        storyline = response.css("#titleStoryLine > div[itemprop='description'] > p::text").extract()
        storyline = "\n".join([x.strip() if x else "" for x in storyline])

        image = convert_photo(response.css("div.poster > a > img::attr(src)")
                              .extract_first().strip(), "film-list")

        url = self.replaceText(response.url.replace(self.base_url, ''), '?')

        item = FilmDetail()
        item.update({"film_id": re.sub(r"title.+?", "", url).strip("/")})
        item.update({"film_title": name})
        item.update({"film_description_short": short_description})
        item.update({"film_director": person.get("director")})
        item.update({"film_writer": person.get("writer") if "writer" in person else person.get("writers")})
        item.update({"film_stars": person.get("stars") if "stars" in person else person.get("star")})
        item.update({"film_creator": person.get("creators") if "creators" in person else person.get("creator")})
        item.update({"film_rating": rating})
        item.update({"film_genre": genre})
        item.update({"film_photo": image})
        item.update({"film_year": year})
        item.update({"film_length": length})
        item.update({"film_type": type})
        item.update({"film_date_release": time})
        item.update({"film_content_rating": contentRating})
        item.update({"film_storyline": storyline})

        yield item

    def get_year_movie(self, component):
        year = dict()
        if component:
            component = re.sub("[()]", "", component).replace(u"\u2013", "5432112345") if component else ""
            component = re.sub("[^0-9.]+", "", component).split("5432112345")

            if len(component) > 1:
                component[1] = int(component[1]) if component[1] != '' else 'On Going'

            if len(component) > 0 and component[0] != "":
                year = {'start': int(component[0]), 'end': component[1]} if len(component) > 1 \
                    else {'start': int(component[0]), 'end': int(component[0])}
            else:
                year = {'start': 'Info Not Found', 'end': 'Info Not Found'}

            return year
        else:
            return {'start': 'Info Not Found', 'end': 'Info Not Found'}

    def replaceText(self, text, keyword):
        there = re.compile(re.escape('{}'.format(keyword)) + '.*')
        return there.sub('', text)