#! /usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Jett.Hu'
import json
import datetime
from peewee import *
from env_crawl.settings import *

db_name = DB_DBNAME
db_host = DB_HOST
db_user = DB_USER
db_pwd = DB_PASSWORD
db_port = int(DB_PORT)
pg_db = PostgresqlDatabase(db_name, user=db_user, password=db_pwd, host=db_host, port=db_port)


class BaseModel(Model):
    class Meta:
        database = pg_db

    def __str__(self):
        result = {}
        for k, v in self.__data__.items():
            if k in ('update_time', 'create_time'):
                result[k] = v.strftime('%Y-%m-%d %H:%M:%S')
            else:
                result[k] = v
        return json.dumps(result)


class EnvCompany(BaseModel):
    name = CharField(max_length=50)
    province = CharField(max_length=20, null=True)
    area = CharField(max_length=50, null=True)
    syear = IntegerField()

    web_id = CharField(max_length=50, null=True)
    entertypename = CharField(max_length=50, null=True)
    legal_person_code = CharField(max_length=50, null=True)
    legal_person = CharField(max_length=20, null=True)
    industry = CharField(max_length=20, null=True)
    address = CharField(max_length=255, null=True)
    url = CharField(max_length=255, null=True, default="")
    create_time = DateTimeField(default=datetime.datetime.now)
    update_time = DateTimeField(default=datetime.datetime.now)

    class Meta:
        indexes = (
            # name/syear指定唯一的多列索引.
            (('name', 'syear', 'province', 'area'), True),
        )


class MonitorPoint(BaseModel):
    company = ForeignKeyField(EnvCompany, related_name='monitor_points', on_delete='CASCADE')
    name = CharField(max_length=100, default="")
    syear = IntegerField()
    code = CharField(max_length=100, default="", null=True)
    point_type = CharField(max_length=100, null=True)
    release_mode = CharField(max_length=100, default="", null=True)
    release_type = CharField(max_length=100, default="", null=True)
    release_destination = CharField(max_length=150, default="", null=True)
    delegation = BooleanField(default=True)
    delegation_company = CharField(max_length=100, default="", null=True)
    quality_control = CharField(max_length=1500, default="", null=True)
    position_picture = CharField(max_length=300, default="", null=True)
    position_picture_url = CharField(max_length=600, default="", null=True)
    device_name = CharField(max_length=400, default="", null=True)
    create_time = DateTimeField(default=datetime.datetime.now)
    update_time = DateTimeField(default=datetime.datetime.now)


class MonitorInfo(BaseModel):
    company = ForeignKeyField(EnvCompany, related_name='c_monitor_infos', on_delete='CASCADE')
    monitor = ForeignKeyField(MonitorPoint, related_name='p_monitor_infos', on_delete='CASCADE')
    name = CharField(max_length=60, default="")
    frequency = CharField(max_length=250, default="")  # hour, 2hour, day, week, month, quarter
    frequency_src = CharField(max_length=250, default="", null=True)  # 每小时一次，每两小时一次，每天，周，月，季，半年，年
    point_type = CharField(max_length=50, default="", null=True)  # air, water, noise
    max_value = CharField(max_length=50, default="")
    min_value = CharField(max_length=50, default="")
    max_unit = CharField(max_length=50, default="")
    min_unit = CharField(max_length=50, default="")
    source = CharField(max_length=255, default="")  # 排放标准
    way = CharField(max_length=100, default="")  # auto, manual
    publish_due = CharField(max_length=50, default="", null=True)
    index_type = CharField(max_length=50, default="")  #
    monitor_code = CharField(max_length=100, default="")  # pollutionFactorCode igCode
    syear = IntegerField()
    device_name = CharField(max_length=50, default="", null=True)
    create_time = DateTimeField(default=datetime.datetime.now)
    update_time = DateTimeField(default=datetime.datetime.now)


class Results(BaseModel):
    re_company = ForeignKeyField(EnvCompany, related_name='c_results', on_delete='CASCADE')
    re_monitor = ForeignKeyField(MonitorPoint, related_name='p_results', on_delete='CASCADE')
    re_monitor_info = ForeignKeyField(MonitorInfo, related_name='i_results', on_delete='CASCADE')
    re_type = CharField(max_length=10, default="day")  # hour, day
    monitor = CharField(max_length=255, default="", null=True)
    monitor_info = CharField(max_length=255, default="", null=True)
    company = CharField(max_length=255, default="", null=True)
    threshold = CharField(max_length=255, default="", null=True)
    monitor_value = CharField(max_length=250, default="")
    unit = CharField(max_length=255, default="", null=True)
    min_cal_value = CharField(max_length=250, default="")
    max_cal_value = CharField(max_length=250, default="")
    release_time = CharField(max_length=30, default="")  # release_time same with website
    monitor_way = CharField(max_length=10, default="auto")  # auto, manual
    exceed_flag = CharField(max_length=30, default="")
    exceed_type = CharField(max_length=30, default="")
    times = CharField(max_length=30, default="")
    pollution_type = CharField(max_length=50, default="")
    pollution_go = CharField(max_length=50, default="")
    data_status = CharField(max_length=100, default="")
    remark = CharField(max_length=200, default="")
    province = CharField(max_length=100, default="")
    zs_value = CharField(max_length=250, default="", null=True)
    discharge_amount = CharField(max_length=250, default="", null=True)
    syear = IntegerField()
    pub_time = DateTimeField(null=True)  # release_time with format save db
    create_time = DateTimeField(default=datetime.datetime.now)
    update_time = DateTimeField(default=datetime.datetime.now)


if __name__ == '__main__':
    pg_db.connect()
    pg_db.create_tables([EnvCompany, MonitorPoint])
    pg_db.close()
