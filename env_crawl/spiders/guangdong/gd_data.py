# -*- coding: utf-8 -*-
import scrapy
import os
import re
import requests
from env_crawl.items import *
from env_crawl.settings import *
from env_crawl.utils.RedisHelper import *
from datetime import timedelta

syear = SYEAR
province = '广东'


class GdDataSpider(scrapy.Spider):
    name = 'guangdong.data'
    allowed_domains = ['app.gdep.gov.cn']
    start_urls = ['https://app.gdep.gov.cn/epinfo/']

    def start_requests(self):
        # 从数据库中获取公司名和web_id进行监测信息爬取
        companies = EnvCompany.select().where(EnvCompany.province == province, EnvCompany.syear == syear)
        for company in companies:
            url = "https://app.gdep.gov.cn/epinfo/selfmonitor/getSelfmonitorMonitor/{0}?ename={1}&year={2}".format(
                company.web_id, company.name, syear)
            yield scrapy.Request(url, meta={'company': company})

    def parse(self, response):
        meta = response.meta
        company = meta['company']
        # 获取监测点位和监测点位的code
        searchObj = re.findall(r"var\s+optionmplist\s+=\s+\$\(.<option value='([^']+)' >([^<]+)<\/option>.\)",
                               response.text)
        if searchObj is None:
            return
        for group in searchObj:
            point_code = group[0]
            point_name = group[1]

            monitor_point_dict = {
                "company": company.id,
                "code": point_code,
                "name": point_name
            }
            if "水" in point_name:
                monitor_point_dict["point_type"] = "water"
            elif "气" in point_name:
                monitor_point_dict["point_type"] = "air"
            elif "声" in point_name:
                monitor_point_dict["point_type"] = "noise"
            else:
                monitor_point_dict["point_type"] = ""
            monitor_point_dict['syear'] = syear
            monitor_point_item = MonitorPointItem(**monitor_point_dict)
            point = monitor_point_item.insert_or_update()

            monitor_info_url = "https://app.gdep.gov.cn/epinfo/selfmonitor/findMiinfo?mpid={0}".format(point_code)
            monitor_info_html = requests.get(monitor_info_url)
            monitor_info_lists = json.loads(monitor_info_html.text)
            for info in monitor_info_lists:
                if info["mitec"] != "":
                    if int(info["mitec"]) == 1:
                        mode = "manual"  # 手动监测
                        frequency = "day"
                    else:
                        mode = "auto"  # 自动监测
                        frequency = "hour"
                    print("监测因子:{}".format(info["miname"]))
                    monitor_info_dict = {"name": info["miname"], "max_unit": info["unit"], "monitor_code": info["miid"],
                                         "way": mode, "company": company, "monitor": point, "syear": syear}
                    monitor_info_item = MonitorInfoItem(**monitor_info_dict)
                    monitor_info_instance = monitor_info_item.insert_or_update()
                else:
                    monitor_info_dict = {}
                    print("点位：{0}没有监测因子".format(point_name))
                    continue
                dataType = 'all'
                begin_time = getStartTime(syear, province, company.id, dataType, mode, frequency, point.id,
                                          monitor_info_instance.id)
                print(begin_time.strftime("%Y-%m-%d %H:%M:%S").center(80, '-'))
                end_time = getEndTime(syear)
                print(end_time.strftime("%Y-%m-%d %H:%M:%S").center(80, '-'))
                if end_time < begin_time:
                    print("{}目前为止，该部分数据已经全部爬取".format(company.name))
                while begin_time < end_time:
                    start_day = begin_time.strftime("%Y-%m-%d")
                    one_month = begin_time + timedelta(days=HISTORY_BEFORE)
                    end_day = one_month.strftime("%Y-%m-%d")
                    # meta_data = {"year": syear, "company": company, "data_type": dataType, "monitor_point": point,
                    #              "monitor_info": monitor_info_dict, "way": mode, "start": start_day,
                    #              "end": end_day}
                    print("monitor_info:{0}{1}".format(monitor_info_dict["name"], point.name))
                    if mode == "manual":
                        print("{0}~{1}manual".format(start_day, end_day).center(80, '-'))
                        getResultsOneCompanyManual(syear, company, dataType, point, monitor_info_dict, mode,
                                                   start_day, end_day)
                    else:
                        print("{0}~{1}auto".format(start_day, end_day).center(80, '-'))
                        getResultsOneCompanyAuto(syear, company, dataType, point, monitor_info_dict, mode,
                                                 start_day, end_day)
                    begin_time += timedelta(days=HISTORY_BEFORE)

    def parse_manual(self, response):
        print(response.text)
        pass

    def parse_auto(self, response):
        print(response.text)
        pass

    def parse_detail(self, response):
        pass


def getResultsOneCompanyManual(inputYear, company, dataType, monitor_point, monitor_info, way, startTime,
                               endTime, page=1):
    print("start get manual results:", company.name)
    print("monitor_info:", monitor_info["name"], monitor_point.name)
    url = "https://app.gdep.gov.cn/epinfo/selfmonitor/findAccountInfo"
    para_dct = {"mpId": monitor_point.code, "miId": monitor_info["name"], "startime": startTime, "endtime": endTime,
                "directid": company.web_id, "id": company.web_id, "year": inputYear, "page": page}
    html_doc = requests.post(url, para_dct)
    if html_doc:
        result_lists = json.loads(html_doc.text)
        total_numbers = int(result_lists["map"]["Total"])  # 或得的是数据的总条数，然后根据总条数来计算获得总页数
        total_pages = total_numbers / 24
        if total_numbers % 24 != 0:
            total_pages += 1
        print("total_pages:", total_pages)
        monitor_info_instance = None
        if total_pages > 0 and "list" in result_lists.keys():
            queryList = []
            for r in result_lists["list"]:
                monitor_info["frequency"] = "day"
                monitor_info["way"] = way
                monitor_info["max_value"] = r["standardValue"]
                monitor_info["syear"] = inputYear

                monitor_info_item = MonitorInfoItem(**monitor_info)
                monitor_info_instance = monitor_info_item.insert_or_update()

                release_time_list = re.findall('\d+', r["monitorTime"])  # 监测时间
                try:
                    release_time = release_time_list[0] + "-" + release_time_list[1] + "-" + release_time_list[2]
                except:
                    release_time = r["creaTime"].split(" ")[0]
                result_dict = {"re_company": company, "company": company.name, "re_monitor": monitor_point,
                               "re_type": monitor_info_instance.frequency, "re_monitor_info": monitor_info_instance,
                               "monitor": monitor_point.name, "monitor_info": monitor_info_instance.name,
                               "province": province, "release_time": release_time,
                               "data_status": r["monitorResult"]}
                try:
                    if r["monitorType"] == "2":
                        result_dict["remark"] = '作废。' + r["invalidreason"].strip()
                    elif 'invalidreason' in r.keys():
                        if r["invalidreason"] == "停产":
                            result_dict["remark"] = "停产"
                        else:
                            result_dict["remark"] = r["invalidreason"].strip()
                except Exception as e:
                    print(e)
                    print(traceback.format_exc())
                try:
                    result_dict["pubtime"] = datetime.strptime(result_dict["release_time"] + " 00:00:00",
                                                               '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    print("错误的时间：", release_time)
                    continue
                result_dict["threshold"] = r["standardValue"].strip()
                result_dict["unit"] = monitor_info_instance.max_unit
                result_dict["monitor_way"] = way
                result_dict["monitor_value"] = r["monitorValue"].strip()
                result_dict["exceed_flag"] = r["monitorResult"].strip()
                if result_dict["exceed_flag"] == "达标":
                    result_dict["exceed_type"] = 0
                else:
                    result_dict["exceed_type"] = 1
                queryList.append(result_dict)
            savePagedata(province, company, syear, queryList, dataType, way, "day", monitor_point.id,
                         monitor_info_instance.id)
            # 因为结果可能不止一页，经过判断是否翻页
            if page < total_pages:
                getResultsOneCompanyManual(inputYear, company, dataType, monitor_point, monitor_info, way, startTime,
                                           endTime, page + 1)
        else:
            # 在这里如果不进行监测因子的处理，没有监测结果的话就会丢失监测因子的信息
            monitor_info["frequency"] = "day"
            monitor_info["way"] = way
            # DBTools.createMonitorInfo(inputYear, monitor_info)
            monitor_info_item = MonitorInfoItem(**monitor_info)
            monitor_info_item.insert_or_update()
            print("该时间段没有数据")
            print("-" * 50)


def getResultsOneCompanyAuto(inputYear, company, dataType, monitor_point, monitor_info, way, startTime,
                             endTime, page=1):
    print("start get auto results:", company.name)
    print("monitor_info:", monitor_info["name"], monitor_point.name)
    url = "https://app.gdep.gov.cn/epinfo/selfmonitor/findOM3"
    para_dct = {"mpId": monitor_point.code, "miId": monitor_info["monitor_code"], "startime": startTime,
                "endtime": endTime, "miinfoname": monitor_info["name"], "directid": company.web_id,
                "id": company.web_id, "year": inputYear, "page": page}
    html_doc = requests.post(url, para_dct)
    if html_doc:
        result_lists = json.loads(html_doc)
    pass
