# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from datetime import datetime
from env_crawl.settings import SQL_DATE_FORMAT, SQL_DATETIME_FORMAT


class EnvCrawlItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    desc = scrapy.Field()
    img = scrapy.Field()


class Company(scrapy.Item):
    """{'entername': '一汽-大众汽车有限公司佛山分公司', 'areacode': '440605',
        'directid': '5D2EC82E-5586-47B8-A898-403086D6C4CA', 'ifreadonly': 1, 'state': 1,
        'monitorDirectId': '7cba45bc-0153-1000-e000-1a08ac15189d', 'myear': 2018, 'entertypename': '危险废物企业',
        'areaName': '佛山市', 'entertype': '6', 'onoff': '0', 'id': 'da1ed812-f767-11e7-9743-005056b616b0',
        'orgcode': '579740701'}"""
    company_name = scrapy.Field()
    company_code = scrapy.Field()
    province = scrapy.Field()
    area = scrapy.Field()
    myear = scrapy.Field()
    entertypename = scrapy.Field()

    def get_insert_sql(self):
        sql = """
            INSERT INTO company(company_name,company_code,province,area,myear,entertypename, crawl_time) VALUES(%s,%s,%s,%s,%s,%s,%s)
        """
        values = (self['company_name'], self['company_code'], self['province'], self['area'], self['myear'],
                  self['entertypename'], datetime.now().strftime(SQL_DATETIME_FORMAT))
        return sql, values
