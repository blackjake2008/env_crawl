# -*- coding: utf-8 -*-
import scrapy
import os
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
        companies = Company.get_company_by_province(province, syear)
        for company in companies:
            company_item = Company.select_to_item(company)
            url = "https://app.gdep.gov.cn/epinfo/selfmonitor/getSelfmonitorMonitor/{0}?ename={1}&year={2}".format(
                company_item.company_id_web, company_item.company_name, syear)
            return [scrapy.Request(url, meta={'id': company[0]})]

    def parse(self, response):
        pass
