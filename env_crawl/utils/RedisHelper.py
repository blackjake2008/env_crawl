#! /usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Jett.Hu'
import redis
from env_crawl.settings import REDIS_URL
from datetime import datetime, date

pool = redis.ConnectionPool.from_url(REDIS_URL)
RD = redis.Redis(connection_pool=pool)


def getStartTime(inputYear, province, company, point_name, factor_name, dataType, way, frequency):
    """

    :param inputYear: 爬取年份
    :param company: 公司id
    :param point_name: 监测点名
    :param factor_name: 监测因子名
    :param dataType: 数据类型：history|realtime
    :param way: 监测方式：auto|manual
    :param frequency: 频率：hour|day
    :return:
    """
    skey = "{0}:{1}:{2}:{3}:{4}:{5}:{6}:{7}".format(inputYear, province, company.id, dataType,
                                                    point_name, factor_name, way, frequency)
    print(skey)
    redis_time = RD.get(skey)
    if redis_time:
        print("get time from redis:", redis_time)
        try:
            crawl_start_time = datetime.strptime(redis_time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            crawl_start_time = datetime(inputYear, 1, 1)
    else:
        crawl_start_time = datetime(inputYear, 1, 1)
        RD.set(skey, crawl_start_time.strftime("%Y-%m-%d %H:%M:%S"))
    return crawl_start_time
