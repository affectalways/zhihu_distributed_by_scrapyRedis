# -*- coding: utf-8 -*-
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#
# 导入时间
import datetime
# 日志路径
import os

SPIDER_MODULES = ['zhihu_distributed_by_scrapyRedis.spiders']
NEWSPIDER_MODULE = 'zhihu_distributed_by_scrapyRedis.spiders'

COOKIES_ENABLED = True
# USER_AGENT = 'scrapy-redis (+https://github.com/rolando/scrapy-redis)'

DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
SCHEDULER_PERSIST = True
# SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderPriorityQueue"
SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderQueue"
# SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderStack"

ITEM_PIPELINES = {
    'zhihu_distributed_by_scrapyRedis.pipelines.ExamplePipeline': 300,
    'zhihu_distributed_by_scrapyRedis.pipelines.RedisPipeline': 400,
}

LOG_LEVEL = 'DEBUG'

# Introduce an artifical delay to make use of parallelism. to speed up the
# crawl.
DOWNLOAD_DELAY = 1.6

'''
    redis
'''
REDIS_HOST = '101.132.163.103'
# REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_PARAMS = {}
REDIS_PARAMS['password'] = '970630'
REDIS_ENCODING = "UTF-8"
REDIS_AUTH = {'password': '970630'}

'''
    Mysql
'''
MYSQL_HOST = '101.132.163.103'
MYSQL_PORT = 3306
MYSQL_DATABASE = 'zhihu'
MYSQL_USER = 'root'
MYSQL_PASSWORD = '970630'

'''
    代理池
'''
# 不知道下面有几个有效地
# 设置代理池
PROXIES = [
    {'ip_port': '60.163.121.203:9000', 'name_password': None},
    {'ip_port': '115.171.203.8:9000', 'name_password': None},
    {'ip_port': '112.250.65.222:53281', 'name_password': None},
    {'ip_port': '202.117.120.242:8080', 'name_password': None},
    {'ip_port': '180.118.247.57:9000', 'name_password': None},
    {'ip_port': '118.193.107.178:80', 'name_password': None},
    {'ip_port': '222.74.225.231:3128', 'name_password': None},
    {'ip_port': '111.3.108.44:8118', 'name_password': None},
    {'ip_port': '118.254.150.150:3128', 'name_password': None},
    {'ip_port': '115.226.9.2:3128', 'name_password': None},
    {'ip_port': '121.8.243.51:8888', 'name_password': None},
    {'ip_port': '114.99.94.232:9000', 'name_password': None},
    {'ip_port': '120.27.195.59:9999', 'name_password': None},
    {'ip_port': '117.90.1.107:9000', 'name_password': None},
]

'''
    设置请求头的User-Agent
'''
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Opera/9.80(WindowsNT6.1;U;en)Presto/2.8.131Version/11.11',
    'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;Maxthon2.0)',
    'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;TencentTraveler4.0)',
    'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;TheWorld)',
    'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;360SE)',
]

'''
    请求头
'''
ZHIHU_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Cache-Control": "max-age=0",
    "Referer": "https://www.zhihu.com/",
    "Host": "www.zhihu.com",
    "Upgrade-Insecure-Requests": "1",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    "Accept-Language": "zh-CN,zh;q=0.8",
}

'''
    日志，每天生成日志
'''

LOG_ENABLED = True
LOG_ENCODING = 'UTF-8'
LOG_LEVEL = 'INFO'
time = datetime.datetime.now()
logPath = os.path.dirname(os.path.abspath(__file__)) + '/log/'
LOG_FILE = logPath + '%s-%s-%s_running.log' % (time.year, time.month, time.day)

'''
    下载中间件
'''
DOWNLOADER_MIDDLEWARES = {
    'zhihu_distributed_by_scrapyRedis.middlewares.UserAgentsDownloaderMiddleware': 300,
    'zhihu_distributed_by_scrapyRedis.middlewares.ProxiesDownloaderMiddleware': 301,
}

'''
    pipelines
'''
ITEM_PIPELINES = {
    'zhihu_distributed_by_scrapyRedis.pipelines.ZhihuPipeline': 302,
}


