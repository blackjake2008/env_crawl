# -*- coding: utf-8 -*-
import scrapy
import os
import re
import requests
from env_crawl.items import *
from env_crawl.settings import *
from env_crawl.utils.RedisHelper import *
from datetime import timedelta

syear = SYEAR
province = '广东'


class GdDataSpider(scrapy.Spider):
    name = 'guangdong.data'
    allowed_domains = ['app.gdep.gov.cn']
    start_urls = ['https://app.gdep.gov.cn/epinfo/']

    def start_requests(self):
        # 从数据库中获取公司名和web_id进行监测信息爬取
        companies = EnvCompany.select().where(EnvCompany.province == province, EnvCompany.syear == syear)
        for company in companies:
            url = "https://app.gdep.gov.cn/epinfo/selfmonitor/getSelfmonitorMonitor/{0}?ename={1}&year={2}".format(
                company.web_id, company.name, syear)
            yield scrapy.Request(url, meta={'company': company})

    def parse(self, response):
        meta = response.meta
        company = meta['company']
        # 获取监测点位和监测点位的code
        searchObj = re.findall(r"var\s+optionmplist\s+=\s+\$\(.<option value='([^']+)' >([^<]+)<\/option>.\)",
                               response.text)
        if searchObj is None:
            return
        for group in searchObj:
            point_code = group[0]
            point_name = group[1]

            monitor_point_dict = {
                "company": company.id,
                "code": point_code,
                "name": point_name
            }
            if "水" in point_name:
                monitor_point_dict["point_type"] = "water"
            elif "气" in point_name:
                monitor_point_dict["point_type"] = "air"
            elif "声" in point_name:
                monitor_point_dict["point_type"] = "noise"
            else:
                monitor_point_dict["point_type"] = ""
            monitor_point_dict['syear'] = syear
            monitor_point = MonitorPointItem(**monitor_point_dict)
            point = monitor_point.insert_or_update()

            monitor_info_url = "https://app.gdep.gov.cn/epinfo/selfmonitor/findMiinfo?mpid={0}".format(point_code)
            monitor_info_html = requests.get(monitor_info_url)
            monitor_info_lists = json.loads(monitor_info_html.text)
            for info in monitor_info_lists:
                if info["mitec"] != "":
                    if int(info["mitec"]) == 1:
                        mode = "manual"  # 手动监测
                        frequency = "day"
                    else:
                        mode = "auto"  # 自动监测
                        frequency = "hour"
                    print("监测因子:{}".format(info["miname"]))
                    monitor_info_dict = {"name": info["miname"], "max_unit": info["unit"], "monitor_code": info["miid"],
                                         "way": mode, "company": company.name, "monitor": point}
                else:
                    monitor_info_dict = {}
                    print("点位：{0}没有监测因子".format(point_name))
                    continue
                dataType = 'all'
                begin_time = getStartTime(syear, province, id, point_name, info['miname'], dataType, mode, frequency)
                print(begin_time.strftime("%Y-%m-%d %H:%M:%S").center(80, '-'))
                end_time = getEndTime(syear)
                print(end_time.strftime("%Y-%m-%d %H:%M:%S").center(80, '-'))
                if end_time < begin_time:
                    print("{}目前为止，该部分数据已经全部爬取".format(company.name))
                while begin_time < end_time:
                    start_day = begin_time.strftime("%Y-%m-%d")
                    end_day = end_time.strftime("%Y-%m-%d")
                    meta_data = {"year": syear, "company": company, "data_type": dataType, "monitor_point": point,
                                 "monitor_info": monitor_info_dict, "way": mode, "start": start_day,
                                 "end": end_day}
                    print("monitor_info:{0}{1}".format(monitor_info_dict["name"], point.name))
                    if mode == "manual":
                        print("{0}~{1}manual".format(start_day, end_day).center(80, '-'))
                        print("start get manual results:{}".format(company.name))
                        url = "https://app.gdep.gov.cn/epinfo/selfmonitor/findAccountInfo"
                        form_data = {
                            "mpId": point.code, "miId": monitor_info_dict["name"], "startime": start_day,
                            "endtime": end_day, "directid": company.web_id, "id": company.web_id,
                            "year": syear, "page": 1
                        }
                    else:
                        print("{0}~{1}auto".format(start_day, end_day).center(80, '-'))
                        print("start get auto results:{}".format(company.name))
                        url = "https://app.gdep.gov.cn/epinfo/selfmonitor/findOM3"
                    begin_time += timedelta(days=HISTORY_BEFORE)

    def parse_manual(self, response):
        pass

    def parse_auto(self, response):
        pass

    def parse_detail(self, response):
        pass
