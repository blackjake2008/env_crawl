# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class EnvCrawlItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    desc = scrapy.Field()
    img = scrapy.Field()


class CompanyDirectInfo(scrapy.Item):
    areaName = scrapy.Field()
    areacode = scrapy.Field()
    directid = scrapy.Field()
    entername = scrapy.Field()
    entertype = scrapy.Field()
    entertypename = scrapy.Field()
    id = scrapy.Field()
    ifreadonly = scrapy.Field()
    monitorDirectId = scrapy.Field()
    myear = scrapy.Field()
    onoff = scrapy.Field()
    orgcode = scrapy.Field()
    state = scrapy.Field()
