# -*- coding: utf-8 -*-
import scrapy
import os
import re
import requests
from env_crawl.items import *
from env_crawl.settings import *

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
            yield scrapy.Request(url, meta={'id': company.id, 'company': company.name})

    def parse(self, response):
        meta = response.meta
        id = meta['id']
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
                "company": id,
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
                    print(info["miname"])
                    monitor_info_dict = {}
                    monitor_info_dict["name"] = info["miname"]
                    monitor_info_dict["max_unit"] = info["unit"]
                    monitor_info_dict["monitor_code"] = info["miid"]
                    monitor_info_dict["way"] = mode
                    monitor_info_dict["company"] = company
                    monitor_info_dict["monitor"] = point
                else:
                    monitor_info_dict = {}
                    print("点位：{0}没有监测因子".format(point_name))
                    continue

        pass

    def parse_detail(self, response):
        pass
