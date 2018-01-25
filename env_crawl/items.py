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
    legal_person_code = scrapy.Field()
    legal_person = scrapy.Field()
    industry = scrapy.Field()
    address = scrapy.Field()

    def get_insert_sql(self):
        sql = """
            INSERT INTO company(company_name,company_code,province,area,myear,entertypename,legal_person_code,
            legal_person,industry,address,crawl_time) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        values = (self['company_name'], self['company_code'], self['province'], self['area'], self['myear'],
                  self['entertypename'], self['legal_person_code'], self['legal_person'], self['industry'],
                  self['address'], datetime.now().strftime(SQL_DATETIME_FORMAT))
        return sql, values

    def get_updata_sql(self):
        sql = """
            UPDATE company SET company_code=%s,entertypename=%s,legal_person_code=%s,legal_person=%s,
            industry=%s,address=%s,updata_time=%s 
            WHERE company_name=%s AND province=%s AND area=%s AND myear=%s
        """
        values = (self['company_code'], self['entertypename'], self['legal_person_code'], self['legal_person'],
                  self['industry'], self['address'], datetime.now().strftime(SQL_DATETIME_FORMAT),
                  self['company_name'], self['province'], self['area'], self['myear'])
        return sql, values
