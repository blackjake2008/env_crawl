# -*- coding: utf-8 -*-
import scrapy
import json
from env_crawl.items import Company


class GdepSpider(scrapy.Spider):
    name = 'gdep'
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
        formdata = {'ename': '', 'year': '2018'}
        for i in range(1, 2):  # TODO page_num+1
            yield scrapy.FormRequest(
                url=url % i,
                formdata=formdata,
                callback=self.parse_companies
            )

    def parse_companies(self, response):
        data = json.loads(response.body_as_unicode())
        companies = data['listDirectinfoVo']
        for company in companies:
            c_info = Company()
            c_info['province'] = '广东'
            c_info['area'] = company.get('areaName', '')
            c_info['company_name'] = company.get('entername', '')
            c_info['company_code'] = company.get('monitorDirectId', '')
            c_info['entertypename'] = company.get('entertypename', '')
            c_info['myear'] = company.get('myear', '')
            yield c_info
            # base_info_url = "https://app.gdep.gov.cn/epinfo/selfmonitor/getEnterpriseInfo/{0}?ename={1}&year={2}"
            # base_info_url = base_info_url.format(c_info['company_code'], c_info['company_name'], c_info['myear'])
            # yield scrapy.Request(url=base_info_url, callback=self.parse_base_info)

    def parse_base_info(self, response):
        pass
