# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class ActressList(scrapy.Item):
    actress_id = scrapy.Field()
    actress_link = scrapy.Field()
    actress_name = scrapy.Field()
    actress_photo = scrapy.Field()

class ActressDetail(scrapy.Item):
    actress_id = scrapy.Field()
    actress_name = scrapy.Field()
    actress_height = scrapy.Field()
    actress_category = scrapy.Field()
    actress_filmography = scrapy.Field()

class ActressBio(scrapy.Item):
    actress_id = scrapy.Field()
    actress_bio = scrapy.Field()
    actress_birth = scrapy.Field()
    actress_height = scrapy.Field()
    actress_personal_detail = scrapy.Field()

class ActressPhoto(scrapy.Item):
    actress_id = scrapy.Field()
    actress_media = scrapy.Field()

class FilmList(scrapy.Item):
    film_id = scrapy.Field()
    film_year = scrapy.Field()
    film_title = scrapy.Field()
    film_photo = scrapy.Field()
    film_length = scrapy.Field()
    film_rating = scrapy.Field()
    film_genre = scrapy.Field()
    film_description_short = scrapy.Field()

class FilmDetail(scrapy.Item):
    film_id = scrapy.Field()
    film_title = scrapy.Field()
    film_description_short = scrapy.Field()
    film_director = scrapy.Field()
    film_writer = scrapy.Field()
    film_stars = scrapy.Field()
    film_photo = scrapy.Field()
    film_creator = scrapy.Field()
    film_year = scrapy.Field()
    film_type = scrapy.Field()
    film_length = scrapy.Field()
    film_rating = scrapy.Field()
    film_genre = scrapy.Field()
    film_date_release = scrapy.Field()
    film_content_rating = scrapy.Field()
    film_storyline = scrapy.Field()


class FilmSynopsis(scrapy.Item):
    film_id = scrapy.Field()
    film_synopsis = scrapy.Field()

class FilmPhoto(scrapy.Item):
    film_id = scrapy.Field()
    film_media = scrapy.Field()