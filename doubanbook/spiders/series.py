# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from doubanbook.items import SeriesItem
import redis
import re


r = redis.Redis(host="localhost", port=6379, db=0)
num_re = re.compile("^[\d]+")


class SeriesSpider(RedisSpider):
    name = "series"
    allowed_domains = ["douban.com"]

    def parse(self, response):
        series = SeriesItem()
        if response.url[-1] is '/':
            _ = -2
        else:
            _ = -1
        series["series_id"] = int(num_re.search(
            response.url.split("/")[_]).group(0))
        r.srem("series:set", series["series_id"])
        content = response.xpath("//div[@id='content']")
        series["series_name"] = content.xpath("h1/text()").extract()[0]
        series["book_num"] = int(content.xpath(
            "//div[@class='clear-both']/text()").extract()[-1].strip())
        series["recommend_num"] = int(num_re.search(
            content.xpath(
                "//div[@class='article']/div[@class='rel-info']/" +
                "div[@class='rec-sec']/" + "span[@class='rec-num']/text()"
            ).extract()[0]).group()
        )
        contri_list = content.xpath("//div[@class='aside']/a/@href").extract()
        series["contribute_list"] = [_.split("/")[-2] for _ in contri_list]
        _people_base_url = "http://www.douban.com/people/%s"
        for _people in series["contribute_list"]:
            if not r.sismember("people:set", _people):
                r.sadd("people:set", _people)
                r.rpush("people:start_urls", _people_base_url % _people)
        book_list = content.xpath(
            "//div[@class='article']//ul[@class='subject-list']/" +
            "li[@class='subject-item']//div[@class='info']/h2/a/@href"
        ).extract()
        series["book_list"] = [0] * series["book_num"]
        if series["book_num"] > 10:
            series["book_list"][0:10] = [
                int(_.split("/")[-2]) for _ in book_list]
            _baseurl = "http://book.douban.com/series/38?page=%d"
            return [scrapy.Request(
                _baseurl % 2, callback=self.parse_extra_page,
                meta={"series": series})]
        else:
            series["book_list"][:] = [int(_.split("/")[-2]) for _ in book_list]
            _book_base_url = "http://book.douban.com/subject/%d"
            for _book in series["book_list"]:
                if not r.sismember("book:set", _book):
                    r.sadd("book:set", _book)
                    r.rpush("book:start_urls", _book_base_url % _book)
            return series

    def parse_extra_page(self, response):
        """Parse extra pages if number of books exceeds 10.

        :response: TODO
        :returns: TODO

        """
        _content = response.xpath("//div[@id='content']")
        _book_list = _content.xpath(
            "//div[@class='article']//ul[@class='subject-list']/" +
            "li[@class='subject-item']//div[@class='info']/h2/a/@href"
        ).extract()
        _series = response.meta["series"]
        _num = len(_series["book_list"]) / 10 + 1
        _idx = int(response.url.split("=")[-1])
        print len(_series["book_list"]), _num
        _series["book_list"][(_idx - 1) * 10:(_idx - 1) * 10 + len(_book_list)]\
            = [int(_.split("/")[-2]) for _ in _book_list]
        if _idx < _num:
            _baseurl = "http://book.douban.com/series/38?page=%d"
            return [scrapy.Request(
                _baseurl % (_idx + 1), callback=self.parse_extra_page,
                meta={"series": _series})]
        else:
            for _book in _series["book_list"]:
                if not r.sismember("book:set", _book):
                    r.sadd("book:set", _book)
                    r.rpush("book:start_urls", _book_base_url % _book)
            return _series
