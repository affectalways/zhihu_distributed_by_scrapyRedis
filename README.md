# zhihu_distributed_by_scrapyRedis
利用scrapy_redis爬取知乎

利用技术：
    1.scrapy_redis
    2.mysql存储数据
    3.redis存储headers，cookies，zhihu:start_urls
    4.Spider是继承的RedisSpider
    


程序缺陷：
    1.遇到知乎unhuman鉴别，并没有写；只是打开知乎，然后输入非机器验证码后就OK了，感觉比在程序中解决简单（仅本人观点，或许有点可笑）
    2.并不可能爬取知乎全部用户数据，最多一次一次性爬取了120w，然后才被识别出是爬虫

   


