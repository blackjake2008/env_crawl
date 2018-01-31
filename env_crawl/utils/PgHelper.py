#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""数据库操作类"""
__author__ = 'Jett.Hu'
import psycopg2
import logging.handlers

pg_logger = logging.getLogger('PgHelper')
pg_logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s [%(name)s](%(levelname)s): %(message)s')
ch.setFormatter(formatter)
LOG_LEVEL = {'debug': logging.DEBUG, 'info': logging.INFO, 'warning': logging.WARNING, 'error': logging.ERROR,
             'notset': logging.NOTSET, 'critical': logging.CRITICAL}


class PgHelper(object):
    def __init__(self, database_url, level='debug'):
        self.url = database_url
        self.__conn, self.__cur = None, None
        ch.setLevel(LOG_LEVEL.get(level.lower(), logging.DEBUG))
        pg_logger.addHandler(ch)

    def conn_db(self):
        try:
            pg_logger.info('connect to database %s' % self.url)
            self.__conn = psycopg2.connect(self.url)
            self.__cur = self.__conn.cursor()
            return True
        except Exception as e:
            pg_logger.error('Failed to connect to the database!\n' + e)
            self.__conn, self.__cur = None, None
            return False

    def execute(self, sql):
        try:
            self.__cur.execute(sql)
            self.__conn.commit()
            pg_logger.debug('Success execute one sql')
        except Exception as e:
            pg_logger.error(repr(e))
            self.__conn.rollback()

    def __enter__(self):
        if self.conn_db():
            return self
        raise IOError('Failed connect database!')

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        pg_logger.info('Disconnect to database')
        self.__cur.close()
        self.__conn.close()

    def select_one(self, sql):
        try:
            self.__cur.execute(sql)
            return self.__cur.fetchone()
        except Exception as e:
            pg_logger.error(repr(e))
            self.__conn.rollback()

    def select(self, sql):
        try:
            self.execute(sql)
            return self.__cur.fetchall()
        except Exception as e:
            pg_logger.error(repr(e))
            self.__conn.rollback()

    def create(self, sql):
        try:
            self.__cur.execute(sql)
            self.__conn.commit()
        except Exception as e:
            pg_logger.error(repr(e))
            self.__conn.rollback()
