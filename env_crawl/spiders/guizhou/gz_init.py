# -*- coding: utf-8 -*-

import scrapy
import json
from env_crawl.items import CompanyItem
from env_crawl.settings import *
import re

syear = SYEAR


class GzInitSpider(scrapy.Spider):
    name = 'guizhou.init'
    allowed_domains = ['www.gzqyjpjc.com']
    start_urls = ['http://www.gzqyjpjc.com/qyjbxx/']

    def parse(self, response):
        panels = response.css('.qysy_name.panel')
        for p in panels:
            area = p.css(".qy_stitle::text").extract_first()
            area_comps = p.css(".qy_name_list li a")
            for comp in area_comps:
                href = comp.css('::attr("href")').extract_first()
                name = comp.css('::text').extract_first()
                meta = {
                    'url': response.urljoin(href),
                    'area': area,
                    'name': name
                }
                yield scrapy.Request(url=meta['url'], meta=meta, callback=self.parse_company)

    def parse_company(self, response):
        c_info = CompanyItem()
        c_info['syear'] = syear
        c_info['province'] = '贵州'
        c_info['url'] = response.meta['url']
        c_info['area'] = response.meta['area']
        c_info['name'] = response.meta['name']
        c_info['web_id'] = re.search("\?firmId=(.*)\"\)", response.text).group(1)
        trs = response.css("table.hb_qyjc tr")
        c_info['industry'] = trs[3].css("td")[3].css("::text").extract_first()
        c_info['legal_person'] = trs[2].css("td")[3].css("::text").extract_first()
        c_info['address'] = trs[1].css("td")[1].css("::text").extract_first()
        yield c_info
