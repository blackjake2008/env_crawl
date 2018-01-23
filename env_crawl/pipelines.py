# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import psycopg2


class EnvCrawlPipeline(object):
    def process_item(self, item, spider):
        return item


class PsqlPipeline(object):
    pg_uri = 'postgresql://postgres:postgres@localhost:5432/env_crawl'

    def __init__(self):
        self.connection = psycopg2.connect(PsqlPipeline.pg_uri)
        self.connection.autocommit = True
        self.cursor = None

    def open_spider(self, spider):
        self.cursor = self.connection.cursor()

    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()

    def process_item(self, item, spider):
        insert_sql, values = item.get_insert_sql()
        self.cursor.execute(insert_sql, values)
        return item
