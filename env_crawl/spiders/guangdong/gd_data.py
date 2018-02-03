# -*- coding: utf-8 -*-
import scrapy
import os
import re
import requests
from env_crawl.items import *

syear = int(os.environ.get("YEAR"))
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
            monitor_point.insert_or_update()

            monitor_info_url = "https://app.gdep.gov.cn/epinfo/selfmonitor/findMiinfo?mpid={0}".format(point_code)
            monitor_info_html = requests.get(monitor_info_url)
            monitor_info_lists = json.loads(monitor_info_html)


        pass

    def parse_detail(self, response):
        pass
