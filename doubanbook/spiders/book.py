# -*- coding: utf-8 -*-
from scrapy_redis.spiders import RedisSpider
from doubanbook.items import DoubanbookItem
import redis
import re

number_re = re.compile('([\d]+)')
url_bookid = re.compile('http://book.douban.com/subject/([\d]+)')
url_series = re.compile('http://book.douban.com/series/([\d]+)')
image_id = re.compile('http://img[\d]+.douban.com/lpic/s([\d]+).jpg')
info_trans = {
    u'出版社:': 'press',
    u'副标题:': 'subtitle',
    u'原作名:': 'origin_name',
    u'出版年:': 'year',
    u'页数:': 'pages',
    u'定价:': 'price',
    u'装帧:': 'binding',
    u'统一书号:': 'csbn',
    u'ISBN:': 'isbn'

}
r = redis.Redis(host='localhost', port=6379, db=0)


class BookSpider(RedisSpider):
    name = "book"
    allowed_domains = ["douban.com"]

    def parse(self, response):
        book = DoubanbookItem()
        book['book_id'] = int(url_bookid.search(response.url).group(1))
        # book['book_id'] = int(response.url.split('/')[-1])
        book['title'] = response.xpath(
            '//h1/span/text()').extract()[0]
        self.parse_article(book, response.xpath("//div[@class='article']"))
        self.parse_aside(book, response.xpath("//div[@class='aside']"))
        return book

    def parse_article(self, book, response):
        """help parse article div part of the page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        self.parse_info(book, response.xpath("//div[@id='info']"))
        self.parse_interest(book, response.xpath("//div[@id='interest_sectl']"))
        book['image_id'] = response.xpath(
            '//div[@id="mainpic"]/a/@href').extract()[0]
        book['image_id'] = book['image_id'].split('/')[-1][1:-4]
        self.parse_related_info(
            book, response.xpath("div[@class='related_info']"))

    def parse_aside(self, book, response):
        """help parse aside div part of the page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        self.parse_buyinfo(book, response)
        self.parse_borrow_list(book, response)
        self.parse_versions(book, response)
        self.parse_in_doulist(book, response)
        self.parse_num_read(book, response)

    def parse_info(self, book, response):
        """help parse info div in the page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        book['authors'] = response.xpath(
            'span/a/text()').extract()
        book['series_id'] = response.xpath('a/@href').extract()
        if len(book['series_id']) == 0:
            book['series_id'] = -1
        else:
            book['series_id'] = int(book['series_id'][0].split('/')[-1])
            r.lpush('series:start_urls', str(book['series_id']))
        label_list = response.xpath(
            'span[@class="pl"]/text()').extract()
        label_list = [label.strip()
                      for label in label_list if label.strip() != u'']
        if u'丛书:' in label_list:
            label_list.remove(u'丛书:')
        data_list = response.xpath('text()').extract()
        data_list = [data.strip() for data in data_list if data.strip() != u'']
        assert(len(label_list) == len(data_list))
        for i in xrange(len(label_list)):
            book[info_trans[label_list[i]]] = data_list[i]
        book['translators'] = response.xpath(
            'span/a/text()').extract()

    def parse_interest(self, book, response):
        """help parse interest_sectl div part of the page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        if response.xpath('//span[@class="color_gray"]').extract() ==\
                [u'目前无人评价']:
            book['rate_num'] = 0
            book['rate_score'] = 0
        elif response.xpath(
            '//div[@class="rating_sum"]/span/a[@href="collections"]/text()'
        ).extract()[0].strip() == u'评价人数不足':
            book['rate_num'] = 0
            book['rate_score'] = 0
            r.lpush('collections:start_urls', str(book['book_id']))
        else:
            book['rate_num'] = int(response.xpath(
                '//span[@property="v:votes"]/text()'
            ).extract()[0].strip())
            book['rate_score'] = float(
                response.xpath(
                    '//strong/text()'
                ).extract()[0].strip()
            )
            r.lpush('collections:start_urls', book['book_id'])
        book['rate_star'] = response.xpath(
            '//span[@class="rating_per"]/text()'
        ).extract()
        book['rate_star'] = [float(per[:-1]) for per in book['rate_star']]

    def parse_related_info(self, book, response):
        """help parse related_info div part of the page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        self.parse_intro(book, response)
        self.parse_author_intro(book, response)
        self.parse_content(book, response)
        self.parse_tags(book, response)
        self.parse_comments(book, response)
        self.parse_reviews(book, response)
        self.parse_annotation(book, response)
        self.parse_discussion(book, response)

    def parse_intro(self, book, response):
        """help parse intro part of page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        intro = response.xpath('//div[@class="indent" and @id="link-report"]')
        temp = intro.xpath('//span[@class="all hidden"]')
        if len(temp) != 0:
            intro = temp[0]
        book['intro'] = intro.xpath('//div[@class="intro"]/p/text()').extract()

    def parse_author_intro(self, book, response):
        """help parse author_intro part of page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        author_intro = response.xpath('//div[@class="indent "]')
        temp = author_intro.xpath('//span[@class="all hidden "]')
        if len(temp) != 0:
            author_intro = temp[0]
        book['author_intro'] = author_intro.xpath(
            '//div[@class="intro"]/p/text()').extract()

    def parse_content(self, book, response):
        """help parse content part of page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        content = response.xpath(
            '//div[@class="indent" and @id="dir_%d_full"]' % book['book_id'])
        if len(content) == 0:
            content = response.xpath(
                '//div[@class="indent" and @id="dir_%d_short"]' %
                book['book_id'])
        book['content'] = content.xpath('text()').extract()[:-2]

    def parse_tags(self, book, response):
        """help parse tags part of page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        tags_num = response.xpath(
            '//div[@id="db-tags-section"]/h2/span/text()').extract()
        if len(tags_num) != 0:
            tags_num = tags_num[0]
        book['tags_num'] = number_re.search(tags_num).group(1)
        book['tags_list'] = response.xpath(
            '//div[@class="indent"]/span/a[@class="  tag"]/text()').extract()

    def parse_user_like(self, book, response):
        """help parse user_like_also part of page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        book['user_like_also'] = response.xpath(
            '//div[@id="db-rec-section"]/div/dl/dt/a/@href').extract()
        book['user_like_also'] = [url.split('/')[-2]
                                  for url in book['user_like_also']]

    def parse_comments(self, book, response):
        """help parse comments part of page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        comments_num = response.xpath(
            '//div[@class="mod-hd"]//span[@class="pl"]/a/text()').extract()
        if len(comments_num) != 0:
            book['comments_num'] = int(
                number_re.search(comments_num[0]).group(1))
            r.lpush('comments:start_urls', str(book['book_id']))
        else:
            book['comments_num'] = 0

    def parse_reviews(self, book, response):
        """help parse reviews in the page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        reviews_num = response.xpath(
            '//div[@id="reviews"]//span[@class="pl"]/a/' +
            'span[@property="v:count"]/text()').extract()
        if len(reviews_num) != 0:
            book['reviews_num'] = int(reviews_num[0])
            r.lpush('reviews:start_url', str(book['book_id']))
        else:
            book['reviews_num'] = 0

    def parse_annotation(self, book, response):
        """help parse annotation part of page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        annotations_num = response.xpath(
            '//div[@class="ugc-mod reading-notes"]//span[@class="pl"]/a/' +
            'span[@property="v:count"]/text()'
        ).extract()
        if len(annotations_num) != 0:
            book['annotations_num'] = int(annotations_num[0])
            r.lpush('annotations:start_url', str(book['book_id']))
        else:
            book['annotations_num'] = 0

    def parse_discussion(self, book, response):
        """help parse discussion part of page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        has_discussion = response.xpath(
            '//*[@id="db-discussion-section"]/p/a').extract()
        if len(has_discussion) != 0:
            book['has_discussion'] = True
            r.lpush('discussion:start_urls', book['series_id'])
        else:
            book['has_discussion'] = False

    def parse_buyinfo(self, book, response):
        """help parse buyinfo div part of page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        if len(response.xpath('div[@id="buyinfo-printed"]')) != 0:
            r.lpush('buyinfo:start_urls', str(book['book_id']))

    def parse_borrow_list(self, book, response):
        """help parse borrow_list div part of page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        book['borrow_list'] = response.xpath(
            'div[@id="borrowinfo"]/ul/li/a/text()').extract()

    def parse_versions(self, book, response):
        """TODO: Docstring for parse_versions.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        versions = response.xpath(
            "h2/span[@class='pl']/a[contains(@href, 'works')]")
        if len(versions) != 0:
            book['versions_num'] = int(number_re.search(
                versions.xpath("text()").extract()[0]).group(1))
            book['works_id'] = int(number_re.search(
                versions.xpath("@href").extract()[0]).group(1))
        else:
            book['versions_num'] = 0
            book['works_id'] = -1

    def parse_in_doulist(self, book, response):
        """help parse in_doulist in the page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        doulist = response.xpath(
            "h2/span[@class='pl']/a[contains(@href, 'doulist')]")
        if len(doulist) != 0:
            book['in_doulist'] = True
            r.lpush('book_doulist:start_urls', book['book_id'])
        else:
            book['in_doulist'] = False

    def parse_num_read(self, book, response):
        """help parse num_read part in the page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        num_read = response.xpath("div[@id='collector']/p/a/text()").extract()
        if len(num_read) == 3:
            book['num_reading'] = int(number_re.search(num_read[0]).group(1))
            book['num_read'] = int(number_re.search(num_read[1]).group(1))
            book['num_want_read'] = int(number_re.search(num_read[2]).group(1))
        else:
            book['num_reading'] = 0
            book['num_read'] = 0
            book['num_want_read'] = 0