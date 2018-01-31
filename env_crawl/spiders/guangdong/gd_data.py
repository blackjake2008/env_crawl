# -*- coding: utf-8 -*-
import scrapy
import os
import re
import requests
from env_crawl.items import Company
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
syear = os.environ.get("YEAR")
province = '广东'


class GdDataSpider(scrapy.Spider):
    name = 'guangdong.data'
    allowed_domains = ['app.gdep.gov.cn']
    start_urls = ['https://app.gdep.gov.cn/epinfo/']

    def start_requests(self):
        # 从数据库中获取公司名和web_id进行监测信息爬取
        companies = Company.get_company_by_province(province, syear)
        for company in companies:
            company_item = Company.select_to_item(company)
            url = "https://app.gdep.gov.cn/epinfo/selfmonitor/getSelfmonitorMonitor/{0}?ename={1}&year={2}".format(
                company_item['company_id_web'], company_item['company_name'], syear)
            yield scrapy.Request(url, meta={'id': company[0], 'company': company_item['company_name']})

    def parse(self, response):
        id = response.meta['id']
        company = requests.meta['company']
        # 获取监测点位和监测点位的code
        searchObj = re.findall(r"var\s+optionmplist\s+=\s+\$\(.<option value='([^']+)' >([^<]+)<\/option>.\)",
                               response.text)
        if searchObj is not None:
            for group in searchObj:
                point_code = group[0]
                point_name = group[1]
                monitor_info_url = "https://app.gdep.gov.cn/epinfo/selfmonitor/findMiinfo?mpid={0}".format(point_code)
                # yield scrapy.Request(monitor_info_url, callback=self.parse_detail)
                monitor_info_html = requests.get(monitor_info_url)
                point = None
                monitor_point_dict = {
                    "company": company,
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

        pass

    def parse_detail(self, response):
        pass
