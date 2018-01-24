# -*- coding: utf-8 -*-
import random
import time

import redis
from scrapy import log
from scrapy.utils.project import get_project_settings


class Tools(object):
    # 获取验证码类型 及 url
    @staticmethod
    def get_captcha():
        # 获取验证码url
        now_time = int(time.time() * 1000)
        # 验证码类型，cn为倒立的中文，en为字母数字
        # lang_list = ['en', 'cn']
        # en用于开发，主要是简单
        lang_list = ['en']
        lang = random.choice(lang_list)
        print('验证码类型：%s' % lang)
        # 为什么要这样获取验证码/
        # 因为有时验证码会隐藏，不固定，一会儿input，一会div
        captcha_url = 'https://www.zhihu.com/' + 'captcha.gif?r=%d&type=login&lang=%s' % (now_time, lang)
        return lang, captcha_url

    @staticmethod
    def url_is_tuple(url):
        isurl = url
        if isinstance(url, tuple):
            isurl = url[0]
        return isurl


'''
    需要修改，改成url_token，name,gender存到mongodb或者mysql数据库中
    而url_token只需要存到redis数据库中即可。
    不过我倾向于mysql数据库
'''


class RedisConnection(object):
    def __init__(self):
        REDIS_HOST = get_project_settings().get('REDIS_HOST')
        REDIS_PORT = get_project_settings().get('REDIS_PORT')
        REDIS_AUTH = get_project_settings().get('REDIS_AUTH')
        # 使用redis数据库
        # 存储url_token（set类型）去重，以便存储到MySQL中没有重复的
        # 存储request headers的内容，也就是z_c0，xsrf等等
        # redis://[:password]@localhost:6379/0
        pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_AUTH['password'])
        self.redis_connection = redis.StrictRedis(connection_pool=pool)
        # self.redis_connection = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_AUTH['password'],
        #                                           db=0)

    def lpush(self, name, *values):
        self.redis_connection.lpush(name, *values)

    # set，mysql根据返回值判断值是否已经存在
    def set_url(self, url_token):
        # 若是值已经存在，sadd返回0；值不存在，sadd返回1
        # set 存储所有的url_token
        flag = self.redis_connection.sadd('url_set', url_token)
        log.msg('url_set(set)正在放入 %s, 存在标识符0/1 Y/N %d' % (url_token, flag), level=log.INFO)
        # list存储url_token，但是中途会读取pop，所以需要set去重
        if flag == 1:
            log.msg('url(list)正在放入 %s' % url_token, level=log.INFO)
            # self.redis_connection.lpush('url', url_token)
        return flag

    def get_url(self):
        if self.redis_connection.llen('zhihu:start_urls'):
            # str类型
            # type(self.redis_url_connection.spop('url'))
            url = self.redis_connection.lpop('zhihu:start_urls')
            log.msg('zhihu:start_urls (list)中lpop出 %s' % url, level=log.INFO)
            return url
        else:
            log.msg("所有用户数据已被获取完毕！！\n程序终止！", level=log.CRITICAL)
            # os._exit(0)

    # 存储headers
    def set_headers(self, headers):
        log.msg('headers(string)存入headers', level=log.INFO)
        self.redis_connection.set("headers", headers)

    # 返回headers
    def get_headers(self):
        headers = self.redis_connection.get('headers')
        log.msg('从 headers(string)读取headers', level=log.INFO)
        return headers

    # 保存cookies
    def set_cookiejar(self, cookiejar):
        log.msg('cookiejar(string)存入cookiejar', level=log.INFO)
        self.redis_connection.set('cookiejar', cookiejar)

    # 返回cookies
    def get_cookiejar(self):
        cookiejar = self.redis_connection.get('cookiejar')
        log.msg('从cookiejar(string)读取cookiejar', level=log.INFO)
        return cookiejar


if __name__ == '__main__':
    pass
    # redisConnection = RedisConnection()
    # # print type(redisConnection.get_url())
    # print redisConnection.get_url()
