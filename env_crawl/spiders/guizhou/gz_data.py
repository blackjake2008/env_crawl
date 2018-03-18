#! /usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from env_crawl.items import *
from env_crawl.settings import *
from env_crawl.utils.RedisHelper import *
from datetime import timedelta

syear = SYEAR
province = '贵州'


class GzDataSpider(scrapy.Spider):
    name = 'guizhou.data'
    allowed_domains = ['www.gzqyjpjc.com']
    start_urls = ['http://www.gzqyjpjc.com/qyjbxx/']

    def start_requests(self):
        # 从数据库中获取公司名和web_id进行监测信息爬取
        companies = EnvCompany.select().where(EnvCompany.province == province, EnvCompany.syear == syear)
        for company in companies:
            begin_time = getStartTime(syear, province, company.id, "all", "auto", "", "", "")
            print(begin_time.strftime("%Y-%m-%d %H:%M:%S").center(80, '-'))
            end_time = getEndTime(syear)
            print(end_time.strftime("%Y-%m-%d %H:%M:%S").center(80, '-'))
            if end_time < begin_time:
                print("{}目前为止，该部分数据已经全部爬取".format(company.name))
            while begin_time < end_time:
                begin_time += timedelta(days=1)
                datetime_str = begin_time.strftime("%Y-%m-%d")
                firmId = company.web_id.split("a")[1]
                form_data = {
                    "firmId": firmId,
                    "m": "sdData",
                    "datetime": datetime_str
                }
                url = "http://www.gzqyjpjc.com/search/data2.do"
                yield scrapy.FormRequest(url=url, formdata=form_data, meta={'company': company, "datatype": 1})

    def parse(self, response):
        meta = response.meta
        company = meta['company']
        datatype = meta["datatype"]
        try:
            json_str = json.loads(response.text)
        except ValueError:
            print(company.name, "异常数据")
            return None
        if not json_str:
            return None
        time_str = json_str["date"]
        datas = json_str["datas"]
        for point_name in datas:
            monitor_point_dict = {
                "company": company.id,
                "name": point_name,
                "syear": syear
            }
            if "水" in point_name:
                monitor_point_dict["point_type"] = "water"
            elif "气" in point_name:
                monitor_point_dict["point_type"] = "air"
            elif "声" in point_name:
                monitor_point_dict["point_type"] = "noise"
            else:
                monitor_point_dict["point_type"] = ""

            monitor_point_item = MonitorPointItem(**monitor_point_dict)
            monitor_point = monitor_point_item.insert_or_update()

            monitor_results = datas[point_name]['data']
            monitor_info_instance = None
            queryList = []
            for monitor_name, oneresult in monitor_results.items():
                print("监测点位:{}， 监测项:{}， 监测信息:{}".format(point_name, monitor_name, oneresult))
                monitor_info = {
                    "company": company.id,
                    'monitor': monitor_point.id,
                    'name': monitor_name,
                    'max_value': oneresult['standard'].strip("<"),
                    'max_unit': oneresult['unit'],
                    'frequency': 'day',
                    'syear': syear,
                    'way': 'auto'
                }

                monitor_info_item = MonitorInfoItem(**monitor_info)
                monitor_info_instance = monitor_info_item.insert_or_update()

                result_dict = {"re_company": company, "company": company.name, "re_monitor": monitor_point,
                               "re_type": monitor_info_instance.frequency, "re_monitor_info": monitor_info_instance,
                               "monitor": monitor_point.name, "monitor_info": monitor_info_instance.name,
                               "province": province, "release_time": datetime.strptime(time_str, '%Y.%m.%d'),
                               'max_cal_value': oneresult['unit']}

                try:
                    float(oneresult['strength'])
                    result_dict['monitor_value'] = oneresult['strength'].strip()
                except:
                    result_dict['monitor_value'] = None

                if oneresult['isOk'] != u"--":  # 不是达标
                    result_dict['exceed_flag'] = True  # 是否超标
                else:
                    result_dict['exceed_flag'] = False

                if result_dict["exceed_flag"] == "False":
                    result_dict["exceed_type"] = 0
                else:
                    result_dict["exceed_type"] = 1

                beishu = oneresult['overTimes'].strip()
                try:
                    result_dict['times'] = float(beishu)
                except:
                    result_dict['times'] = float(0)

                if datatype == 0:
                    result_dict['monitor_way'] = "manual"
                else:
                    result_dict['monitor_way'] = "auto"
                result_dict['province'] = province
                result_dict["pub_time"] = result_dict["release_time"]
                queryList.append(result_dict)
            savePagedata(province, company, syear, queryList, datatype, "auto", "day", monitor_point.id,
                         monitor_info_instance.id)
