# -*- coding: utf-8 -*-
from scrapy_redis.spiders import RedisSpider
from doubanbook.items import DoubanbookItem
import redis


class BookSpider(RedisSpider):
    name = "book"
    allowed_domains = ["douban.com"]

    def parse(self, response):
        r = redis.Redis(host='localhost', port=6379, db=0)
        book = DoubanbookItem()
        book['title'] = response.xpath(
            '//*[@id="wrapper"]/h1/span/text()').extract()
        book['series_id'] = response.xpath('//*[@id="info"]/a/@href').extract()
        print book['title']
        r.lpush('series:start_urls', book['series_id'])
        return book
