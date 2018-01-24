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

ROBOTSTXT_OBEY = False

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


# Introduce an artifical delay to make use of parallelism. to speed up the
# crawl.
# DOWNLOAD_DELAY = random.randint(0,4) + round(random.random(), 1)
# 设置的有点低
DOWNLOAD_DELAY = 1.9

'''
    redis
'''
REDIS_HOST = '****************'
# REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_PARAMS = {}
REDIS_PARAMS['password'] = '************'
REDIS_ENCODING = "UTF-8"
REDIS_AUTH = {'password': '**********'}

'''
    Mysql
'''
MYSQL_HOST = '***************'
MYSQL_PORT = 3306
MYSQL_DATABASE = 'zhihu'
MYSQL_USER = 'root'
MYSQL_PASSWORD = '******'

'''
    代理池
'''
# 不知道下面有几个有效地
# 设置代理池
PROXIES = [
    {'ip_port': '180.118.92.218:9000', 'name_password': None},
    {'ip_port': '121.232.144.224:9000', 'name_password': None},
    {'ip_port': '202.194.14.72:8118', 'name_password': None},
    {'ip_port': '218.64.93.208:808', 'name_password': None},
    {'ip_port': '117.43.1.182:808', 'name_password': None},
    {'ip_port': '121.232.144.65:9000', 'name_password': None},
    {'ip_port': '122.96.59.100:80', 'name_password': None},
    {'ip_port': '121.69.70.182:8118', 'name_password': None},
    {'ip_port': '163.125.250.167:8118', 'name_password': None},
    {'ip_port': '121.232.199.227:9000', 'name_password': None},
    {'ip_port': '115.159.0.178:808', 'name_password': None},
    {'ip_port': '180.118.247.136:9000', 'name_password': None},
    {'ip_port': '106.4.137.87:9000', 'name_password': None},
    {'ip_port': '121.232.146.233:9000', 'name_password': None},
    {'ip_port': '121.232.144.122:9000', 'name_password': None},
    {'ip_port': '223.241.79.180:8010', 'name_password': None},
    {'ip_port': '223.241.79.144:8010', 'name_password': None},
    {'ip_port': '223.241.116.17:8010', 'name_password': None},
    {'ip_port': '223.241.117.189:8010', 'name_password': None},
    {'ip_port': '117.90.6.234:9000', 'name_password': None},
    {'ip_port': '117.90.0.134:9000', 'name_password': None},
    {'ip_port': '180.119.65.123:3128', 'name_password': None},
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
