# -*- coding: utf-8 -*-
from scrapy_redis.spiders import RedisSpider


class SeriesSpider(RedisSpider):
    name = "series"
    allowed_domains = ["douban.com"]

    def parse(self, response):
        series_name = response.xpath('//*[@id="content"]/h1/text()').extract()
        print series_name
