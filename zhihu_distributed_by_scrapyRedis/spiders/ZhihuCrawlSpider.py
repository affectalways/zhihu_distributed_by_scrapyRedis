# -*- coding: utf-8 -*-
import json
import os
import re
import sys

import jsonpath
# 将cookiejar转换成dict
import requests
import scrapy
from scrapy import log
from scrapy.http.cookies import CookieJar
from scrapy.utils.project import get_project_settings
from scrapy_redis.spiders import RedisSpider
from zhihu_distributed_by_scrapyRedis.items import ZhihuItem
from zhihu_distributed_by_scrapyRedis.tools import Tools, RedisConnection
from redis import Redis

reload(sys)
sys.setdefaultencoding('UTF-8')


class ZhihuSpider(RedisSpider):
    """Spider that reads urls from redis queue (myspider:start_urls)."""
    name = 'zhihu'
    redis_key = 'zhihu:start_urls'

    redisConnection = RedisConnection()
    # 实例化一个CookieJar对象
    cookiejar = CookieJar()

    # ItemLoader
    # zhIL = None

    def parse(self, response):
        print '++++++++++++++++++++++++++++++++++++++++++++'
        print response.url
        if response.url.find('followers') == -1:
            yield scrapy.Request('https://www.zhihu.com/signup?next=%2F', meta={'cookiejar': 1},
                                 callback=self.parse_first_open_page)
        else:
            print '=' * 30
            url_token = str(response.url).split('/')[-2]
            yield scrapy.Request(response.url, callback=self.gather_follower,
                                 cookies=eval(self.redisConnection.get_cookiejar()),
                                 meta={
                                     'count': 0,
                                     'url_token': url_token,
                                 },
                                 )

    # login_LinkExtractor 调用的callback
    # 1.获取cookie
    # 2.获取_xsrf
    # 3.获取验证码连接，验证码类型
    def parse_first_open_page(self, response):
        _xsrf = str(response.headers['Set-Cookie']).split(';')[0].split('=')[1]
        # 获取验证码类型，url
        captcha_type, captcha_url = Tools.get_captcha()
        # 这里是为了记录cookiejar，望 没漏掉任何东西
        response.meta['cookiejar'] = 1
        yield scrapy.Request(
            url=captcha_url,
            meta={
                'cookiejar': response.meta['cookiejar'],
                '_xsrf': _xsrf,
                'captcha_type': captcha_type,
            },
            callback=self.download_captcha
        )

    # 下载验证码
    # 登录
    def download_captcha(self, response):
        file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/images/captcha.jpg'
        with open(file_path, 'wb') as f:
            f.write(response.body)
        get_project_settings().get('ZHIHU_HEADERS')['X-Xsrftoken'] = response.meta['_xsrf']
        # 开启应用程序，打开图片
        os.system('start ' + file_path)
        yield scrapy.FormRequest(
            url='https://www.zhihu.com/login/phone_num',
            meta={
                'cookiejar': response.meta['cookiejar'],
                # 作为第一个访问的url的标志
                # 'SPECIFIED_FLAG': 1,
                '_xsrf': response.meta['_xsrf'],
            },
            headers=get_project_settings().get('ZHIHU_HEADERS'),
            formdata={
                'captcha_type': response.meta['captcha_type'],
                'phone_num': str(raw_input('please input your phone_num:\n')),
                '_xsrf': response.meta['_xsrf'],
                'password': str(raw_input('please input your password:\n')),
                'captcha': str(raw_input('please input captcha:\n'))
            },
            callback=self.visit_specified_url,
        )

    # 1.处理登录后的页面，获取z_c0，也就是authorization
    # 2.Request访问指定某人的页面，获取这个人的
    def visit_specified_url(self, response):
        # response.status为int类型
        authorization_re = re.compile('z_c0=.*?;')
        authorization = authorization_re.search(str(response.headers)).group().split('=')[1].replace(';', '')
        # 给请求头加上authorization
        get_project_settings().get('ZHIHU_HEADERS')['authorization'] = 'Bearer ' + authorization
        headers = get_project_settings().get('ZHIHU_HEADERS')
        self.redisConnection.set_headers(headers)
        # 使用extract_cookies方法可以提取response中的cookie
        self.cookiejar.extract_cookies(response, response.request)
        # 给cookiejar添加_xsrf
        requests.utils.add_dict_to_cookiejar(self.cookiejar, {'_xsrf': response.meta['_xsrf']})
        # 将cookiejar添加到redis中
        self.redisConnection.set_cookiejar(str(requests.utils.dict_from_cookiejar(self.cookiejar)))
        # 早先在url，url_set中存取第一个要访问的页面，从url中拿出来
        url_token = self.redisConnection.get_url()
        url = "https://www.zhihu.com/people/" + url_token + "/followers"
        # 因为程序运行时不时会出现获取的是tuple错误
        url = Tools.url_is_tuple(url)
        # <class 'scrapy.http.headers.Headers'>
        # type(response.headers)
        # 记录headers，同时将这个headers调用tools的set_cookiejar方法，写入文件

        log.msg("正在访问 %s \n" % url, level=log.INFO)
        # 访问指定的某人的followers页面
        yield scrapy.Request(
            # 访问该页面
            url=url,
            meta={
                # 'cookiejar': requests.utils.cookiejar_from_dict(eval(self.redisConnection.get_cookiejar())),
                # 作为访问的特殊网页的标志，从而区分是访问的指定网页还是随机访问的！不要代码冗余嘛！思路！
                'SPECIFIED_FLAG': 1,
                'url_token': url_token,
                'count': 0,
            },
            headers=headers,
            cookies=eval(self.redisConnection.get_cookiejar()),
            callback=self.gather_follower,
        )

    # 处理每个被访问人的followers页面，同时获取followers数据和page_number
    def gather_follower(self, response):
        followers_number = int(response.xpath(
            '//div[@class="Card FollowshipCard"]//a[last()]//strong/text()').extract()[0].replace(',', ''))
        page_number = followers_number / 20 + 1

        # 若关注人数为0，则从redis中取出另一个用户的url_token访问，callback=该方法
        # 若该用户的关注人数不是0，则访问json页面
        # 获取需要访问多少页json数据
        if not followers_number:
            count = 0
            url_token = self.redisConnection.get_url()
            url = 'https://www.zhihu.com/people/' + url_token + '/followers',
            url = Tools.url_is_tuple(url)
            log.msg('正在访问 %s\n' % url, level=log.INFO)
            yield scrapy.Request(
                url=url,
                meta={
                    'count': count
                },
                cookies=eval(self.redisConnection.get_cookiejar()),
                headers=eval(self.redisConnection.get_headers()),
                callback=self.gather_follower,
            )
        else:
            print 'gather_followe'
            yield scrapy.FormRequest(
                # 获取对应的json
                url='https://www.zhihu.com/api/v4/members/' + response.meta['url_token'] + '/followers',
                method='GET',
                # 每一个新请求，需要自己手动添加headers
                headers=eval(self.redisConnection.get_headers()),
                formdata={
                    'include': 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics',
                    'offset': str(response.meta['count'] * 20),
                    'limit': '20',
                },
                meta={
                    'page_number': page_number,
                    # 'cookiejar': response.meta['cookiejar'],
                    # 'cookiejar': requests.utils.cookiejar_from_dict(eval(self.redisConnection.get_cookiejar())),
                    'count': response.meta['count'] + 1,
                    'url_token': response.meta['url_token'],
                },
                cookies=eval(self.redisConnection.get_cookiejar()),
                callback=self.gather_json_info,
            )

    # 冗余代码一个是从网页中获取数据，一个是从json中获取数据gather_json_info
    def gather_json_info(self, response):
        print '00000000000000000000000000000000000000'
        json_content = json.loads(response.body)
        urls = jsonpath.jsonpath(json_content, '$..data..url_token')
        names = jsonpath.jsonpath(json_content, '$..data..name')
        genders = jsonpath.jsonpath(json_content, '$..data..gender')
        for redis_key_url, redis_field_name, redis_field_gender in zip(urls, names, genders):
            flag = self.redisConnection.set_url(redis_key_url)
            if flag == 0:
                continue
            else:
                item = ZhihuItem()
                item['url_token'], item['name'], item['gender'] = redis_key_url, redis_field_name, redis_field_gender
                url = 'https://www.zhihu.com/people/' + redis_key_url + '/followers'
                self.redisConnection.lpush('zhihu:start_urls', url)
                yield item

        # 判断是否进行下一次json页面的获取Request
        if response.meta['count'] >= response.meta['page_number']:
            count = 0
            # 从数据库中读取，但是这就需要最开始访问关注人数特别多的用户
            url_token = self.redisConnection.get_url()
            url = 'https://www.zhihu.com/people/' + url_token + '/followers'
            url = Tools.url_is_tuple(url)
            log.msg('正在访问 %s \n' % url, level=log.INFO)
            yield scrapy.Request(
                # 访问其他人的首页
                url=url,
                meta={
                    # 'cookiejar': response.meta['cookiejar'],
                    # 'cookiejar': requests.utils.cookiejar_from_dict(eval(self.redisConnection.get_cookiejar())),
                    'url_token': url_token,
                    'count': count,
                },
                cookies=eval(self.redisConnection.get_cookiejar()),
                headers=eval(self.redisConnection.get_headers()),
                callback=self.gather_follower,
            )
        else:
            # 继续访问下一条json
            yield scrapy.FormRequest(
                url='https://www.zhihu.com/api/v4/members/' + response.meta['url_token'] + '/followers',
                method='GET',
                # 每一个新请求，需要自己手动添加headers
                headers=eval(self.redisConnection.get_headers()),
                formdata={
                    'include': 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics',
                    'offset': str(response.meta['count'] * 20),
                    'limit': '20',
                },
                meta={
                    # 'cookiejar': response.meta['cookiejar'],
                    # 'cookiejar': requests.utils.cookiejar_from_dict(eval(self.redisConnection.get_cookiejar())),
                    'page_number': response.meta['page_number'],
                    'count': response.meta['count'] + 1,
                    'url_token': response.meta['url_token'],
                },
                cookies=eval(self.redisConnection.get_cookiejar()),
                callback=self.gather_json_info,
            )
