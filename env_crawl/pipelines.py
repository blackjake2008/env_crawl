# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from env_crawl.models import pg_db


class EnvCrawlPipeline(object):
    def process_item(self, item, spider):
        return item


class PsqlPipeline(object):
    # @classmethod
    # def from_settings(cls, settings):
    #     # cls.pg_uri = settings['DB_URI']
    #     # conn = psycopg2.connect(cls.pg_uri)
    #     # return cls(conn)
    #     pass
    #
    # def __init__(self, conn):
    #     self.connection = conn
    #     self.connection.autocommit = True
    #     self.cursor = None

    def open_spider(self, spider):
        pg_db.connect()
        pass

    def close_spider(self, spider):
        pg_db.close()
        pass

    def process_item(self, item, spider):
        item.insert_or_update()
        return item
