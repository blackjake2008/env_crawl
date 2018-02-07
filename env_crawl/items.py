# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re
import traceback
from env_crawl.models import *
from datetime import datetime


class EnvCrawlItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    desc = scrapy.Field()
    img = scrapy.Field()


class CompanyItem(scrapy.Item):
    """{'entername': '一汽-大众汽车有限公司佛山分公司', 'areacode': '440605',
        'directid': '5D2EC82E-5586-47B8-A898-403086D6C4CA', 'ifreadonly': 1, 'state': 1,
        'monitorDirectId': '7cba45bc-0153-1000-e000-1a08ac15189d', 'myear': 2018, 'entertypename': '危险废物企业',
        'areaName': '佛山市', 'entertype': '6', 'onoff': '0', 'id': 'da1ed812-f767-11e7-9743-005056b616b0',
        'orgcode': '579740701'}"""
    name = scrapy.Field()
    web_id = scrapy.Field()
    province = scrapy.Field()
    area = scrapy.Field()
    syear = scrapy.Field()
    entertypename = scrapy.Field()
    legal_person_code = scrapy.Field()
    legal_person = scrapy.Field()
    industry = scrapy.Field()
    address = scrapy.Field()
    url = scrapy.Field()

    def insert_or_update(self):
        """调用peewee保存或更新数据"""
        try:
            item = EnvCompany.get(EnvCompany.name == self['name'], EnvCompany.province == self['province'],
                                  EnvCompany.area == self['area'], EnvCompany.syear == self['syear'])
            for k in self.keys():
                item.__setattr__(k, self[k])
            item.update_time = datetime.now()
            item.save()
        except DoesNotExist:
            item = EnvCompany.create(**self)
        except:
            item = None
            print(traceback.format_exc())
        return item

    # def get_insert_sql(self):
    #     """返回insert sql语句和item"""
    #     sql = """
    #         INSERT INTO company(company_name,company_id_web,province,area,myear,entertypename,legal_person_code,
    #         legal_person,industry,address,crawl_time) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    #     """
    #     values = (self['company_name'], self['company_id_web'], self['province'], self['area'], self['myear'],
    #               self['entertypename'], self['legal_person_code'], self['legal_person'], self['industry'],
    #               self['address'], datetime.now().strftime(SQL_DATETIME_FORMAT))
    #     return sql, values
    #
    # def get_update_sql(self):
    #     """返回update sql语句和item"""
    #     sql = """
    #         UPDATE company SET company_id_web=%s,entertypename=%s,legal_person_code=%s,legal_person=%s,
    #         industry=%s,address=%s,update_time=%s
    #         WHERE company_name=%s AND province=%s AND area=%s AND myear=%s
    #     """
    #     values = (self['company_id_web'], self['entertypename'], self['legal_person_code'], self['legal_person'],
    #               self['industry'], self['address'], datetime.now().strftime(SQL_DATETIME_FORMAT),
    #               self['company_name'], self['province'], self['area'], self['myear'])
    #     return sql, values
    #
    # @classmethod
    # def get_company_by_province(cls, pro, year):
    #     """获取该省指定年份所有公司"""
    #     sql = "SELECT * from company WHERE province='{0}' AND myear='{1}'".format(pro, year)
    #     with PgHelper(db_url) as pg:
    #         companies = pg.select(sql)
    #     return companies
    #
    # @classmethod
    # def select_to_item(cls, select):
    #     """将select * 结果转换为item"""
    #     item = Company()
    #     item['company_name'] = select[1]
    #     item['company_id_web'] = select[2]
    #     item['province'] = select[3]
    #     item['area'] = select[4]
    #     item['myear'] = select[5]
    #     item['entertypename'] = select[6]
    #     item['legal_person_code'] = select[9]
    #     item['legal_person'] = select[10]
    #     item['industry'] = select[11]
    #     item['address'] = select[12]
    #     return item


class MonitorPointItem(scrapy.Item):
    company = scrapy.Field()
    name = scrapy.Field()
    syear = scrapy.Field()
    code = scrapy.Field()
    point_type = scrapy.Field()
    release_mode = scrapy.Field()
    release_type = scrapy.Field()
    release_destination = scrapy.Field()
    delegation = scrapy.Field()
    delegation_company = scrapy.Field()
    quality_control = scrapy.Field()
    position_picture = scrapy.Field()
    position_picture_url = scrapy.Field()
    device_name = scrapy.Field()

    def insert_or_update(self):
        try:
            item = MonitorPoint.get(MonitorPoint.company == self['company'], MonitorPoint.name == self['name'],
                                    MonitorPoint.point_type == self['point_type'], MonitorPoint.syear == self['syear'])
            for k in self.keys():
                item.__setattr__(k, self[k])
            item.update_time = datetime.now()
            item.save()
        except DoesNotExist:
            item = MonitorPoint.create(**self)
        except:
            item = None
            print(traceback.format_exc())
        return item


class MonitorInfoItem(scrapy.Item):
    company = scrapy.Field()
    monitor = scrapy.Field()
    name = scrapy.Field()
    frequency = scrapy.Field()
    frequency_src = scrapy.Field()
    point_type = scrapy.Field()
    max_value = scrapy.Field()
    min_value = scrapy.Field()
    max_unit = scrapy.Field()
    min_unit = scrapy.Field()
    source = scrapy.Field()
    way = scrapy.Field()
    publish_due = scrapy.Field()
    index_type = scrapy.Field()
    monitor_code = scrapy.Field()
    syear = scrapy.Field()
    device_name = scrapy.Field()

    def insert_or_update(self):
        if 'max_value' in self.keys() and self['max_value']:
            self['max_value'] = re.sub(r'\s+', " ", str(self["max_value"]))
        clean_frequency(self)
        try:
            item = MonitorInfo.get(MonitorInfo.company == self['company'], MonitorInfo.monitor == self['monitor'],
                                   MonitorInfo.name == self['name'], MonitorInfo.way == self['way'],
                                   MonitorInfo.syear == self['syear'])
            for k in self.keys():
                item.__setattr__(k, self[k])
            item.update_time = datetime.now()
            item.save()
        except DoesNotExist:
            item = MonitorInfo.create(**self)
        except:
            item = None
            print(traceback.format_exc())
        return item


class ResultItem(scrapy.Item):
    re_company = scrapy.Field()
    re_monitor = scrapy.Field()
    re_monitor_info = scrapy.Field()
    re_type = scrapy.Field()
    monitor = scrapy.Field()
    monitor_info = scrapy.Field()
    company = scrapy.Field()
    threshold = scrapy.Field()
    monitor_value = scrapy.Field()
    unit = scrapy.Field()
    min_cal_value = scrapy.Field()
    max_cal_value = scrapy.Field()
    release_time = scrapy.Field()
    monitor_way = scrapy.Field()
    exceed_flag = scrapy.Field()
    exceed_type = scrapy.Field()
    times = scrapy.Field()
    pollution_type = scrapy.Field()
    pollution_go = scrapy.Field()
    data_status = scrapy.Field()
    remark = scrapy.Field()
    province = scrapy.Field()
    zs_value = scrapy.Field()
    discharge_amount = scrapy.Field()
    syear = scrapy.Field()
    pub_time = scrapy.Field()

    def insert_or_update(self):
        pass


def clean_frequency(data):
    if 'frequency' in data.keys():
        frequency = data['frequency']
        data['frequency_src'] = frequency
        if re.search("月", frequency):
            frequency = 'month'
        elif re.search("周", frequency):
            frequency = 'week'
        elif re.search("日", frequency):
            frequency = 'day'
        elif re.search("季", frequency):
            frequency = 'quarter'
        elif re.search("半年", frequency):
            frequency = 'halfyear'
        elif re.search("年", frequency):
            frequency = 'year'
        elif re.search("连续", frequency) or re.search("连续监测", frequency) or re.search("时", frequency) or re.search("小时",
                                                                                                                  frequency) or re.search(
            "2小时", frequency):
            frequency = 'hour'

        data['frequency'] = frequency
