# -*- coding:utf-8 -*-
import json
import sys

import scrapy
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider


reload(sys)
sys.setdefaultencoding('utf8')


class MySpider(CrawlSpider):
    name = "example.com"
    allowed_damins = ["www.zhihu.com"]
    start_urls = ["https://www.zhihu.com"]

    headers = {
        'Host': 'www.zhihu.com',
        'Referer': 'http://www.zhihu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'
    }
    rules = ()

    def parse_start_url(self, response):
        print "calling parse_start_url" + "*" * 20
        xsrf = Selector(response).xpath('//input[@name="_xsrf"]/@value').extract()[0]
        self.log(xsrf)
        return scrapy.FormRequest(
            "https://www.zhihu.com/login/phone_num",
            headers=self.headers,
            formdata={'phone_num': '18626427054', 'password': 'wanghj123', 'captcha_type': 'cn', '_xsrf': xsrf},
            callback=self.after_login,
        )

    def after_login(self, response):
        print response.status
        result = json.loads(response.body)
        print(result[u'msg'])
        print "after_login calling........................"

    def start_requests(self):
        print "start_requests calling" + "*" * 20
        yield scrapy.Request("https://www.zhihu.com/#signin")
