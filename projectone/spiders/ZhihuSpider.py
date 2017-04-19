# -*- coding: utf-8 -*-
import scrapy
import json

class ZhihuSpider(scrapy.Spider):
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    headers = {
            'Host': 'www.zhihu.com',
            'Referer': 'http://www.zhihu.com',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36',
        }

    def start_requests(self):
        # 返回值必须是一个序列
        return [scrapy.Request('http://www.zhihu.com/#signin', callback=self.login)]

    def login(self, response):
        print '-------'     # 便于测试
        _xsrf = response.xpath(".//*[@id='sign-form-1']/input[2]/@value").extract()[0]
        print _xsrf
        return [scrapy.FormRequest(
            url = 'http://www.zhihu.com/login/email',    # 这是post的真实地址
            formdata={
                '_xsrf': _xsrf,
                'email': 'xxxxxxxx',    # email
                'password': 'xxxxxxxx',    # password
                'remember_me': 'true',
            },
            headers=self.headers,
            callback=self.check_login,
        )]

    def check_login(self, response):
        if json.loads(response.body)['r'] == 0:
            yield scrapy.Request(
                                'http://www.zhihu.com', 
                                headers=self.headers, 
                                callback=self.page_content,
                                dont_filter=True,    
                                )

    def page_content(self, response):
        with open('first_page.html', 'wb') as f:
            f.write(response.body)
        print 'done'
