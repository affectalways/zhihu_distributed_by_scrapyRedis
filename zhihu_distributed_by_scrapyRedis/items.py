# -*- coding: utf-8 -*-
# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

import scrapy


class ZhihuItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url_token = scrapy.Field()
    name = scrapy.Field()
    # 男1，女0，未填-1
    gender = scrapy.Field()
