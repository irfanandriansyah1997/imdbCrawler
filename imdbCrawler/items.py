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
    actress_category = scrapy.Field()
    actress_filmography = scrapy.Field()
    actress_height = scrapy.Field()

class ActressBio(scrapy.Item):
    actress_id = scrapy.Field()
    actress_height = scrapy.Field()
    actress_birth = scrapy.Field()
    actress_personal_detail = scrapy.Field()
    actress_bio = scrapy.Field()

class ActressPhoto(scrapy.Item):
    actress_id = scrapy.Field()
    actress_media = scrapy.Field()