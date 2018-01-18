# -*- coding: utf-8 -*-
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
from scrapy.utils.project import get_project_settings
import pymysql
import redis


class ZhihuPipeline(object):
    def __init__(self):
        '''
            mysql数据库
        '''
        MYSQL_HOST = get_project_settings().get('MYSQL_HOST')
        MYSQL_PORT = get_project_settings().get('MYSQL_PORT')
        MYSQL_DATABASE = get_project_settings().get('MYSQL_DATABASE')
        MYSQL_USER = get_project_settings().get('MYSQL_USER')
        MYSQL_PASSWORD = get_project_settings().get('MYSQL_PASSWORD')
        self.mysql_connection = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, database=MYSQL_DATABASE,
                                                port=MYSQL_PORT,
                                                password=MYSQL_PASSWORD, charset='utf8')
        self.mysql_cursor = self.mysql_connection.cursor()

    def process_item(self, item, spider):
        data = dict(item)
        sql = 'insert into zhihu (url, name, gender) VALUES (%s, %s, %s)'
        self.mysql_cursor.execute(sql, (
            data['url_token'].encode('UTF-8'), data['name'].encode('UTF-8'), str(data['gender'])))
        self.mysql_connection.commit()
        return item

    def close_spider(self, spider):
        self.mysql_cursor.close()
        self.mysql_connection.close()
