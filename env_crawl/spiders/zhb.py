# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class ZhbSpider(CrawlSpider):
    name = 'zhb'
    allowed_domains = ['www.zhb.gov.cn']
    start_urls = ['http://www.zhb.gov.cn/']

    rules = (
        Rule(LinkExtractor(allow=r'gov.cn'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        i = {}
        # i['domain_id'] = response.xpath('//input[@id="sid"]/@value').extract()
        # i['name'] = response.xpath('//div[@id="name"]').extract()
        # i['description'] = response.xpath('//div[@id="description"]').extract()
        return i
