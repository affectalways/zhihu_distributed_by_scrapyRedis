# coding=utf-8
import json
import os
import re
import sys
from scrapy import log
import jsonpath
import scrapy
from scrapy.utils.project import get_project_settings
from scrapy_redis.spiders import RedisSpider
from zhihu_distributed_by_scrapyRedis.items import ZhihuItem
from zhihu_distributed_by_scrapyRedis.tools import Tools, RedisConnection

reload(sys)
sys.setdefaultencoding('UTF-8')


class ZhihuCrawlSpider(RedisSpider):
    """Spider that reads urls from redis queue (myspider:start_urls)."""
    name = 'zhihuCrawlSpider'
    redis_key = 'zhihuCrawlSpider:start_urls'

    redisConnection = RedisConnection()

    def parse(self, response):
        yield scrapy.Request('https://www.zhihu.com/signup?next=%2F', meta={'cookiejar': 1},
                             callback=self.parse_first_open_page)

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
                # 这里是否需要传递_xsrf，待定
            },
            headers=get_project_settings().get('ZHIHU_HEADERS'),
            formdata={
                'captcha_type': response.meta['captcha_type'],
                'phone_num': str(raw_input('please input your phone_num:\n')),
                # 'phone_num': '17864291830',
                '_xsrf': response.meta['_xsrf'],
                'password': str(raw_input('please input your password:\n')),
                # 'password': 'yangshaoxuan0630',
                'captcha': str(raw_input('please input captcha:\n'))
            },
            callback=self.visit_specified_url,
        )

    # 1.处理登录后的页面，获取z_c0，也就是authorization
    # 2.Request访问指定某人的页面，获取这个人的
    def visit_specified_url(self, response):
        authorization_re = re.compile('z_c0=.*?;')
        authorization = authorization_re.search(str(response.headers)).group().split('=')[1].replace(';', '')
        # 给请求头加上authorization
        get_project_settings().get('ZHIHU_HEADERS')['authorization'] = 'Bearer ' + authorization
        specified_url = "https://www.zhihu.com/people/affectalways.cn/followers"
        # <class 'scrapy.http.headers.Headers'>
        # type(response.headers)
        # 记录headers，同时将这个headers调用tools的set_cookiejar方法，写入文件
        headers = get_project_settings().get('ZHIHU_HEADERS')
        # print type(headers)
        self.redisConnection.set_headers(headers)
        log.msg("正在访问 %s \n" % specified_url, level=log.INFO)
        # 访问指定的某人的followers页面
        yield scrapy.Request(
            # 访问该页面
            url=specified_url,
            meta={
                'cookiejar': response.meta['cookiejar'],
            },
            headers=headers,
            # 交给gather_info处理
            callback=self.gather_specified_url_home_page_info,
        )

    def gather_specified_url_home_page_info(self, response):
        # 获得visit_specified_url访问的url
        redis_key_url = str(response.url).split('/')[-2]
        # 获取visit_specified_url这个被指定页面的所有者的昵称，性别
        redis_field_name = response.xpath(
            '//h1[@class="ProfileHeader-title"]/span[@class="ProfileHeader-name"]/text()').extract()[
            0]
        gender = response.xpath(
            '//div[@class="ProfileHeader-iconWrapper"]//*[name()="svg"]/@class').extract()

        # 这其实不用判断，李开复是男的，以后的gender有点难判断
        if len(gender) > 0:
            # 1 为男， 0为 女
            redis_field_gender = 1 if gender[0].count('fe') > 0 else 0
        else:
            # 未标明性别
            redis_field_gender = -1
        '''
            新添加的，使用pipelines
        '''
        self.redisConnection.set_url(redis_key_url)
        url_token = self.redisConnection.get_url()
        item = ZhihuItem()
        item['url_token'], item['name'], item['gender'] = redis_key_url, redis_field_name, redis_field_gender
        yield item

        # 获取关注者人数
        followers_number = int(
            response.xpath('//div[@class="Card FollowshipCard"]//a[last()]//strong/text()').extract()[0].replace(",",
                                                                                                                 ""))
        count = 0
        # 如果关注人数>0，访问这个指定的人的json页面数据
        if followers_number > 0:
            # 获取json页面的次数
            page_number = followers_number / 20 + 1
            yield scrapy.FormRequest(
                url='https://www.zhihu.com/api/v4/members/' + url_token + '/followers',
                method='GET',
                # 每一个新请求，需要自己手动添加headers
                headers=eval(self.redisConnection.get_headers()),
                # 这是？传递后面的内容
                # offset，count=-1是获取第一个json
                formdata={
                    'include': 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics',
                    'offset': str(20 * count),
                    'limit': '20',
                },
                # 传递count+1，原因是在self.gather_json_info中继续获取下一条json
                meta={
                    'cookiejar': response.meta['cookiejar'],
                    'page_number': page_number,
                    'count': count + 1,
                    'url_token': url_token,
                },
                callback=self.gather_json_info,
            )
        else:
            # 执行另一个人的url
            # 这一条永远执行不了，因为我不会一开始选择没有任何关注人数的人
            pass

    '''
            gather_json_info这个方法仅仅适用于解析json页面
            1.解析上次穿来的json页面的response
            2.判断是否进行下一次json页面的获取Request
        '''

    # 1.处理gather_specified_info传递来的json页面的response
    # 2.获取json页面所有的url_token, name， gender
    def gather_json_info(self, response):
        # 解析json页面，获取对应的url_token,name,gender
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
                yield item

        # 判断是否进行下一次json页面的获取Request
        if response.meta['count'] >= response.meta['page_number']:
            count = 0
            # 从数据库中读取，但是这就需要最开始访问关注人数特别多的用户
            url_token = self.redisConnection.get_url()
            url = 'https://www.zhihu.com/people/' + url_token + '/followers'
            # print url
            log.msg('正在访问 %s \n' % url, level=log.INFO)
            yield scrapy.Request(
                # 访问其他人的首页
                url=url,
                meta={
                    'cookiejar': response.meta['cookiejar'],
                    'url_token': url_token,
                    'count': count,
                },
                headers=eval(self.redisConnection.get_headers()),
                callback=self.visit_others_home_page,
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
                    'cookiejar': response.meta['cookiejar'],
                    'page_number': response.meta['page_number'],
                    'count': response.meta['count'] + 1,
                    'url_token': response.meta['url_token'],
                },
                callback=self.gather_json_info,
            )

    '''
        登录是一定要的，因为有些用户设置的隐私权限，只有登录才能看见！！！！！！
        登录也就是传cookiejar!!!!!
        visit_others_home_page是处理gather_json_info不再获取json数据，而是访问新的用户首页的response
        response中的meta传递count=0，url_token
    '''

    def visit_others_home_page(self, response):
        # 获取用户的关注者人数
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
            log.msg('正在访问 %s\n' % url, level=log.INFO)
            yield scrapy.Request(
                url=url,
                meta={
                    'cookiejar': response.meta['cookiejar'],
                    'count': count
                },
                headers=eval(self.redisConnection.get_headers()),
                callback=self.visit_others_home_page,
            )
        else:
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
                    'page_number': page_number,
                    'cookiejar': response.meta['cookiejar'],
                    'count': response.meta['count'] + 1,
                    'url_token': response.meta['url_token'],
                },
                callback=self.gather_json_info,
            )
