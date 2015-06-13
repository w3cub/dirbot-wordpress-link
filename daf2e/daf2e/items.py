# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Daf2EItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
	link_category = scrapy.Field()
	link_name = scrapy.Field()
	link_url = scrapy.Field()
	link_description = scrapy.Field()
