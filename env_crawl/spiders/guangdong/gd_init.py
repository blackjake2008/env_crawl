# -*- coding: utf-8 -*-
"""
初始化公司基础信息，每年保持最新的一份数据, 每月调度一次
"""
import scrapy
import json
from env_crawl.items import CompanyItem
from env_crawl.settings import *

syear = SYEAR


class GdInitSpider(scrapy.Spider):
    name = 'guangdong.init'
    allowed_domains = ['app.gdep.gov.cn']
    start_urls = ['https://app.gdep.gov.cn/epinfo']

    def parse(self, response):
        try:
            com_num = response.css('.widget-icons.pull-right').re(r'企业总数:(\d+)')[0]
            com_num = int(com_num)
            print(com_num)
            page_num = com_num // 24 + 1
        except:
            page_num = 0
        print(page_num)
        url = 'https://app.gdep.gov.cn/epinfo/region/0/%s'
        formdata = {'ename': '', 'year': str(syear)}
        print("开始初始化广东", syear, "年公司信息")
        for i in range(1, page_num + 1):  # TODO page_num+1
            yield scrapy.FormRequest(
                url=url % i,
                formdata=formdata,
                callback=self.parse_companies
            )

    def parse_companies(self, response):
        data = json.loads(response.body_as_unicode())
        companies = data['listDirectinfoVo']
        for company in companies:
            c_info = CompanyItem()
            c_info['province'] = '广东'
            c_info['url'] = 'https://app.gdep.gov.cn/epinfo'
            c_info['area'] = company.get('areaName', '')
            c_info['name'] = company.get('entername', '')
            c_info['web_id'] = company.get('monitorDirectId', '')
            c_info['entertypename'] = company.get('entertypename', '')
            c_info['syear'] = str(company.get('myear', ''))
            # yield c_info
            base_info_url = "https://app.gdep.gov.cn/epinfo/selfmonitor/getEnterpriseInfo/{0}?ename={1}&year={2}"
            base_info_url = base_info_url.format(c_info['web_id'], c_info['name'], c_info['syear'])
            yield scrapy.Request(url=base_info_url, meta={'company_info': c_info}, callback=self.parse_base_info)

    def parse_base_info(self, response):
        c_info = response.meta['company_info']
        table = response.css('table.in-to')
        tds = table.css('td::text').extract()
        c_info['legal_person_code'] = tds[-4].strip()
        c_info['legal_person'] = tds[-3].strip()
        c_info['industry'] = tds[-2].strip()
        c_info['address'] = tds[-1].strip()
        yield c_info
