#! /usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Jett.Hu'
import redis
import re
import traceback
from env_crawl.settings import REDIS_URL, API_RD_URL
from datetime import datetime, date
from env_crawl.models import Results

pool = redis.ConnectionPool.from_url(REDIS_URL)
RD = redis.Redis(connection_pool=pool)
api_pool = redis.ConnectionPool.from_url(API_RD_URL)
API_RD = redis.Redis(connection_pool=api_pool)


def getStartTime(inputYear, province, company, dataType, way, frequency, point_name, factor_name):
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
    skey = "{0}:{1}:company:{2}:{3}:{4}:{5}:{6}:{7}".format(inputYear, province, company, dataType,
                                                            point_name, factor_name, way, frequency)
    print(skey)
    redis_time = RD.get(skey)
    if redis_time:
        redis_time = str(RD.get(skey), encoding='utf-8')
        print("get time from redis:", redis_time)
        try:
            crawl_start_time = datetime.strptime(redis_time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            crawl_start_time = datetime(inputYear, 1, 1)
    else:
        crawl_start_time = datetime(inputYear, 1, 1)
        RD.set(skey, crawl_start_time.strftime("%Y-%m-%d %H:%M:%S"))
    return crawl_start_time


def getEndTime(inputYear):
    if datetime.now().year == inputYear:
        day = datetime.now().today()
    else:
        day = datetime(inputYear, 12, 31)
    return day


def savePagedata(province, company, inputYear, queryList, dataType, way, frequency, point_name, factor_name):
    if len(queryList) > 0:
        sortedQueryList = sorted(queryList, key=lambda k: k['pubtime'])
        insertFlag = bulkCreateResults(inputYear, sortedQueryList)
        if insertFlag and len(sortedQueryList) > 0:
            print("保存数据成功".center(80, "~"))
            skey = "{0}:{1}:company:{2}:{3}:{4}:{5}:{6}:{7}".format(inputYear, province, company, dataType,
                                                                    point_name, factor_name, way, frequency)
            if way == "manual":
                RD.set(skey, sortedQueryList[-1]['release_time'] + " 00:00:00")
            elif way == "auto":
                RD.set(skey, sortedQueryList[-1]['release_time'])
    else:
        print("该时间段内没有数据或数据不满足条件")


# 保存监测记录
def bulkCreateResults(inputYear, record_list):
    result_list = []
    if record_list is None:
        return False
    if len(record_list) > 0 and (type(record_list[0]) == Results):
        # model object array
        for r in record_list:
            for k in r.dirty_fields:
                if getattr(r, k.name) is None:
                    setattr(r, k.name, '')
        result_list = record_list
    else:
        # hash array
        for r in record_list:
            r["syear"] = inputYear
            for k in r.keys():
                if r[k] is None and k != "pubtime":
                    r[k] = ''
                elif isinstance(r[k], str):
                    r[k] = r[k].strip()
            result_obj = Results(**r)
            result_list.append(result_obj)

    ret = True
    for result in result_list:
        try:
            result.save()
            syncRedis(result)
        except Exception as ex:
            print(traceback.format_exc())
            ret = False
            print("create error:")
            print(result.release_time)
            print(result.monitor)
            print(result.monitor_info)
            print("数据插入数据库出错")
            print(ex)
    return ret


# 同步实时数据到redis数据库中，供API使用
def syncRedis(result):
    if type(result) == Results and result.monitor_way == 'auto' and result.re_type == 'hour':
        try:
            # company_lists
            key = 'cl:{0}:{1}'.format(result.province, result.re_company_id)
            API_RD.hset(key, 'lng', result.re_company.lng)
            API_RD.hset(key, 'lat', result.re_company.lat)
            API_RD.hset(key, 'city', result.re_company.city)
            API_RD.hset(key, 'area', result.re_company.area)
            API_RD.hset(key, 'company_name', result.company)
            API_RD.hset(key, 'company_id', result.re_company_id)

            # monitor_points
            point_type = result.re_monitor.point_type
            if point_type == '' or point_type is None:
                point_type = pollutionType(result.monitor_info)
            key = "mp:" + result.re_company_id + ":" + str(result.re_monitor_id)
            API_RD.hset(key, 'monitor_id', result.re_monitor_id)
            API_RD.hset(key, 'monitor_name', result.monitor)
            API_RD.hset(key, 'monitor_type', point_type)

            # monitor_results
            key = "mr:" + str(result.re_monitor_id) + ":" + str(result.re_monitor_info_id)
            redis_pubtime = API_RD.hget(key, 'monitor_time')
            if redis_pubtime is None or datetime.strptime(redis_pubtime, '%Y-%m-%d %H:%M:%S') < result.pubtime:
                # 当第一次插入数据或有新数据出来的时候才更新
                API_RD.hset(key, 'monitor_value', result.monitor_value)
                API_RD.hset(key, 'monitor_info', result.monitor_info)
                API_RD.hset(key, 'monitor_time', result.pubtime)
                API_RD.hset(key, 'max_value', (result.threshold or result.re_monitor_info.max_value))
                if not (result.zs_value == '' or result.zs_value == '-' or result.zs_value is None):
                    API_RD.hset(key, 'zs_value', result.zs_value)

        except Exception as e:
            print(traceback.format_exc())


# 根据监测因子查找排放类型
def pollutionType(monitor_info):
    fp = open("sql/AutoSQLandCSV/re_type.csv").read().split("\r\n")[1:]
    tp = ["#\n".join(fp)]

    air = map(lambda x: "%s" % [i for i in x.split(",")][0], re.findall(r'.*\,air(?!=#)', tp[0]))
    water = map(lambda x: "%s" % [i for i in x.split(",")][0], re.findall(r'.*\,water(?!=#)', tp[0]))
    point_type = ''
    if monitor_info in air:
        point_type = 'air'
    if monitor_info in water:
        point_type = 'water'
    return point_type
