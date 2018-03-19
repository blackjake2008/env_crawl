#! /usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Jett.Hu'
from scrapy.commands import ScrapyCommand
from env_crawl.settings import REDIS_URL
from scrapy.utils.project import get_project_settings
import redis

pool = redis.ConnectionPool.from_url(REDIS_URL)
RD = redis.Redis(connection_pool=pool)


class Command(ScrapyCommand):
    requires_project = True

    def syntax(self):
        return '[options]'

    def short_desc(self):
        return 'Runs all of the spiders'

    def run(self, args, opts):
        sync_key = RD.get("crawl-status")
        if sync_key is not None:
            return "爬虫程序正在后台运行中!"
        RD.set("crawl-status", 1)

        spider_list = self.crawler_process.spiders.list()
        for name in spider_list:
            self.crawler_process.crawl(name, **opts.__dict__)
        self.crawler_process.start()
        RD.delete("crawl-status")
        return "爬虫任务完成!"
