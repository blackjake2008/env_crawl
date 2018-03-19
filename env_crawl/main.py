#! /usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'Jett.Hu'

from scrapy.cmdline import execute
from env_crawl.settings import REDIS_URL
import redis

pool = redis.ConnectionPool.from_url(REDIS_URL)
RD = redis.Redis(connection_pool=pool)


def run_task():
    sync_key = RD.get("crawl-status")
    if sync_key is not None:
        return "爬虫程序正在后台运行中!"
    RD.set("crawl-status", 1)
    execute(["scrapy", "crawl", "guangdong.init"])
    execute(["scrapy", "crawl", "guangdong.data"])
    execute(["scrapy", "crawl", "guizhou.init"])
    execute(["scrapy", "crawl", "guizhou.data"])
    RD.delete("crawl-status")
    return "爬虫任务完成!"


def test():
    print("hello, world")
