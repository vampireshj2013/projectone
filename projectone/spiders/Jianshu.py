# -*- coding:utf-8 -*-
"""
    简书爬虫
"""

import sys

import scrapy
from time import sleep
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from projectone.items import ProjectoneItem
from threading import current_thread

reload(sys)
sys.setdefaultencoding('utf8')


class JianshuSpider(CrawlSpider):
    name = "jianshu"
    allowed_damins = ["www.jianshu.com"]
    url_prefix = "http://www.jianshu.com/recommendations/users?page="
    url_page = 1
    start_urls = [url_prefix + str(url_page)]

    rules = (
        Rule(LinkExtractor(allow=('^http://www.jianshu.com/users/\w+/followers$',)), callback='gen_next_page_request',
             follow=True),

        Rule(LinkExtractor(allow=('^http://www.jianshu.com/users/\w+/following$',)), callback='gen_next_page_request',
             follow=True),

        Rule(LinkExtractor(allow=('^http://www.jianshu.com/users/\w+$',)), callback='parse_item', follow=True),

        Rule(LinkExtractor(allow=('^http://www.jianshu.com/u/\w+$',)), callback='parse_item', process_links='process')
    )

    def process(self, urllist):
        self.logger.debug("---------------------------------------")

    def gen_next_page_request(self, response):
        url = response.url
        pageStr = "?page="
        if url and len(response.xpath("//div[@id='list-container']/ul/li")):
            self.logger.debug("gen_next_page_request,before url" + url)
            if pageStr in url:
                page = url[url.find(pageStr) + len(pageStr):len(url)]
                page = int(page) + 1
                url = url[0:url.find(pageStr) + len(pageStr)] + str(page)
            else:
                url += pageStr + str(2)

            self.logger.debug(
                "currentThread = " + current_thread().getName() + "gen_next_page_request,after url" + url)
            yield scrapy.Request(url, callback=self.gen_next_page_request)

    def parse_start_url(self, response):
        print "calling parse_start_url" + "*" * 20
        alist = response.xpath('//a[@class="avatar"]/@href').extract()
        if alist:
            # for aEle in alist:
            #     yield scrapy.Request(response.urljoin(aEle))
            JianshuSpider.url_page += 1
            yield scrapy.Request(response.urljoin(JianshuSpider.url_prefix + str(JianshuSpider.url_page)))

    def parse_item(self, response):
        # sleep(5)
        self.logger.info("url****" + response.url)
        item = ProjectoneItem()
        introlist = response.xpath("//div[@class='js-intro']/text()").extract()
        if len(introlist):
            item['intro'] = introlist[0]
        namelist = response.xpath("//a[@class='name']/text()").extract()
        if len(namelist):
            item['name'] = namelist[0]
        return item


"""
todo:
    1.根据follorers,following计算出需要跟进多少页,生成request
    2.根据url计算出user,去重
    3.获取出用户详细信息
"""
