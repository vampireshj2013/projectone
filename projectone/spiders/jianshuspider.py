# -*- coding:utf-8 -*-
import scrapy
from projectone import items


class JianshuSpider(scrapy.Spider):
    name = "jianshuspider"
    allowed_damins = ["www.jianshu.com"]
    url_prefix = "http://www.jianshu.com/recommendations/users?page="
    url_page = 1
    start_urls = [url_prefix + str(url_page)]

    def parse(self, response):
        """
        <a class="avatar" target="_blank" href="/users/5SqsuF">
        """
        self.process_user_list_page(response)

    def process_user_info(self, response):
        """
        进入用户页面之后，处理用户相关信息
        :param response:
        :return:
        """
        self.logger.info("url****" + response.url)
        item = items.ProjectoneItem()
        introlist = response.xpath("//div[@class='js-intro']/text()").extract()
        if len(introlist):
            item['intro'] = introlist[0]
        namelist = response.xpath("//a[@class='name']/text()").extract()
        if len(namelist):
            item['name'] = namelist[0]
        yield item
        followerurllist = response.xpath("//a[re:test(@href,'^/users/\w+/followers$')]/text()")
        followingurllist = response.xpath("//a[re:test(@href,'^/users/\w+/following$')]")
        if len(followerurllist):
            yield scrapy.Request(response.urljoin(followerurllist[0]), callback=self.process_follow)
        if len(followingurllist):
            yield scrapy.Request(response.urljoin(followingurllist[0]), callback=self.process_follow)

    def process_follow(self, response):
        """
        处理粉丝请求和关注请求
        :param response:
        :return:
        """
        userhreflist = response.xpath("//a[@class='avatar']/text()").extract()
        if len(userhreflist):
            for userHref in userhreflist:
                yield scrapy.Request(userHref, callback=self.process_user_info)

        url = response.url
        pagestr = "?page="
        if url and len(response.xpath("//div[@id='list-container']/ul/li")):
            if pagestr in url:
                page = url[url.find(pagestr) + len(pagestr):len(url)]
                page = int(page) + 1
                url = url[0:url.find(pagestr) + len(pagestr)] + str(page)
            else:
                url += pagestr + str(2)
            yield scrapy.Request(url, callback=self.process_follow)

    def process_user_list_page(self, response):
        """
        下一页推荐用户列表
        :param response:
        :return:
        """
        userhreflist = response.xpath("//a[@class='avatar']/text()").extract()
        if userhreflist:
            for userHref in userhreflist:
                yield scrapy.Request(userHref, callback=self.process_user_info)
            JianshuSpider.url_page += 1
            yield scrapy.Request(response.urljoin(JianshuSpider.url_prefix + str(JianshuSpider.url_page)),
                                 callback=self.process_user_list_page)
