# -*- coding: utf-8 -*-
import scrapy


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
        url = 'https://app.gdep.gov.cn/epinfo/region/0/1'
        formdata = {'ename': '', 'year': '2018'}
        yield scrapy.FormRequest(
            url=url,
            formdata=formdata,
            callback=self.parse_companies
        )

    def parse_companies(self, response):
        tbody = response.css('#EnterpriseVo')[0]
        trs = tbody.css('tr.question-in')
        for tr in trs:
            params = tr.css('td a::attr(onclick)').re(r'"(.*?)"')
            print(params[0], params[1])
            key = params[0]
            ename = params[1]
        next_page = response.css('nextPage').extract_first()
        print(next_page)
