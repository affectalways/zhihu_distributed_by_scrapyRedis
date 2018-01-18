# -*- coding: utf-8 -*-
import random
from scrapy.utils.project import get_project_settings
import base64


class UserAgentsDownloaderMiddleware(object):
    def __init__(self):
        self.user_agents = get_project_settings().get('USER_AGENTS')

    def process_request(self, request, spider):
        request.headers.setdefault('User-Agent', random.choice(self.user_agents))


class ProxiesDownloaderMiddleware(object):
    def __init__(self):
        self.proxies = get_project_settings().get('PROXIES')

    def process_request(self, request, spider):
        proxy = random.choice(self.proxies)
        request.headers.setdefault(proxy['ip_port'])
        if proxy['name_password'] is not None:
            name_password = base64.b64encode(proxy['name_password'])
            request.headers['Proxy-Authorization'] = 'Basic ' + name_password
