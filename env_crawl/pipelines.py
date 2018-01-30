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
    @classmethod
    def from_settings(cls, settings):
        cls.pg_uri = settings['DB_URI']
        conn = psycopg2.connect(cls.pg_uri)
        return cls(conn)

    def __init__(self, conn):
        self.connection = conn
        self.connection.autocommit = True
        self.cursor = None

    def open_spider(self, spider):
        self.cursor = self.connection.cursor()

    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()

    def process_item(self, item, spider):
        try:
            insert_sql, values = item.get_insert_sql()
            self.cursor.execute(insert_sql, values)
        except psycopg2.IntegrityError:
            update_sql, values = item.get_update_sql()
            self.cursor.execute(update_sql, values)
        return item
