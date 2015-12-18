# -*- coding: utf-8 -*-
from scrapy_redis.spiders import RedisSpider
from doubanbook.items import DoubanbookItem
import redis
import re


url_bookid = re.compile('http://book.douban.com/subject/([\d]+)')
url_series = re.compile('http://book.douban.com/series/([\d]+)')
info_trans = {
    u'出版社:': 'press',
    u'副标题:': 'subtitle',
    u'原作名:': 'origin_name',
    u'出版年:': 'year',
    u'页数:': 'pages',
    u'定价:': 'price',
    u'装帧:': 'binding',
    u'统一书号:': 'isbn'

}


class BookSpider(RedisSpider):
    name = "book"
    allowed_domains = ["douban.com"]

    def parse(self, response):
        r = redis.Redis(host='localhost', port=6379, db=0)
        book = DoubanbookItem()
        book['book_id'] = int(url_bookid.search(response.url).group(1))
        book['title'] = response.xpath(
            '//*[@id="wrapper"]/h1/span/text()').extract()[0]
        # Info bound
        book['authors'] = response.xpath(
            '//*[@id="info"]/span/a/text()').extract()
        book['series_id'] = response.xpath('//div[id="info"]/a/@href').extract()
        if book['series_id'].empty():
            book['series_id'] = -1
        else:
            book['series_id'] = int(re.search(book['series_id']))
            r.lpush('series:start_urls', book['series_id'])
        label_list = response.xpath(
            '//div[@id="info"]/span[@id="pl"]/text()').extract()
        label_list = [label.strip()
                      for label in label_list if label.strip() != u'']
        if u'丛书:' in label_list:
            label_list.remove(u'丛书:')
        data_list = response.xpath('//div[@id="info"]/text()').extract()
        data_list = [data.strip() for data in data_list if data.strip() != u'']
        assert(len(label_list) == len(data_list))
        for i in xrange(len(label_list)):
            book[label_list[i]] = data_list[i]

        book['translator'] = response.xpath(
            '//div[@id="info"]/span/a/@href').extract()[len(book['authors'])]
        return book
