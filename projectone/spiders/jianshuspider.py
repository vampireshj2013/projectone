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
        userhreflist = response.xpath("//a[@class='avatar']/@href").extract()
        if userhreflist:
            for userHref in userhreflist:
                yield scrapy.Request(response.urljoin(userHref), callback=self.process_user_info)
            JianshuSpider.url_page += 1
            yield scrapy.Request(response.urljoin(JianshuSpider.url_prefix + str(JianshuSpider.url_page)),
                                 callback=self.parse)

    def process_user_info(self, response):
        """
        进入用户页面之后，处理用户相关信息
        :param response:
        :return:
        """
        self.logger.info("url****" + response.url)
        item = items.ProjectoneItem()
        introlist = response.xpath("//div[@class='js-intro']/text()").extract()
        if introlist:
            item['intro'] = introlist[0]
        namelist = response.xpath("//a[@class='name']/text()").extract()
        if namelist:
            item['name'] = namelist[0]
        yield item
        followerurllist = response.xpath("//a[re:test(@href,'^/users/\w+/followers$')]/@href").extract()
        followingurllist = response.xpath("//a[re:test(@href,'^/users/\w+/following$')]/@href").extract()
        if followerurllist:
            yield scrapy.Request(response.urljoin(followerurllist[0]), callback=self.process_follow)
        if followingurllist:
            yield scrapy.Request(response.urljoin(followingurllist[0]), callback=self.process_follow)

    def process_follow(self, response):
        """
        处理粉丝请求和关注请求
        :param response:
        :return:
        """
        userhreflist = response.xpath("//a[@class='avatar']/@href").extract()
        if userhreflist:
            for userHref in userhreflist:
                yield scrapy.Request(response.urljoin(userHref), callback=self.process_user_info)

        url = response.url
        pagestr = "?page="
        if url and response.xpath("//div[@id='list-container']/ul/li/a/@href").extract():
            if pagestr in url:
                page = url[url.find(pagestr) + len(pagestr):len(url)]
                page = int(page) + 1
                url = url[0:url.find(pagestr) + len(pagestr)] + str(page)
            else:
                url += pagestr + str(2)
            yield scrapy.Request(response.urljoin(url), callback=self.process_follow)

    # def process_user_list_page(self, response):
    #     """
    #     下一页推荐用户列表
    #     :param response:
    #     :return:
    #     """
    #     self.logger.info("begin...#######################")
    #     userhreflist = response.xpath("//a[@class='avatar']/@href").extract()
    #     if userhreflist:
    #         for userHref in userhreflist:
    #             yield scrapy.Request(response.join(userHref), callback=self.process_user_info)
    #         JianshuSpider.url_page += 1
    #         yield scrapy.Request(response.urljoin(JianshuSpider.url_prefix + str(JianshuSpider.url_page)),
    #                              callback=self.process_user_list_page)
