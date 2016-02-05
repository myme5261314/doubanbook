# -*- coding: utf-8 -*-
from scrapy_redis.spiders import RedisSpider
from doubanbook.items import DoubanbookItem
import redis
import re

number_re = re.compile("([\d]+)")
# url_bookid = re.compile("http://book.douban.com/subject/([\d]+)")
# url_series = re.compile("http://book.douban.com/series/([\d]+)")
image_id = re.compile("http://img[\d]+.douban.com/lpic/s([\d]+).jpg")
info_trans = {
    u"出版社:": "press",
    u"副标题:": "subtitle",
    u"原作名:": "origin_name",
    u"出版年:": "year",
    u"页数:": "pages",
    u"定价:": "price",
    u"装帧:": "binding",
    u"统一书号:": "csbn",
    u"ISBN:": "isbn"

}
r = redis.Redis(host='localhost', port=6379, db=0)


class BookSpider(RedisSpider):
    name = "book"
    allowed_domains = ["douban.com"]

    def parse(self, response):
        book = DoubanbookItem()
        book["book_id"] = int(number_re.search(response.url).group(1))
        # book["book_id"] = int(response.url.split("/")[-1])
        r.srem("book:set", book["book_id"])
        book["title"] = response.xpath(
            "//h1/span/text()").extract()[0]
        self.parse_article(book, response, response.xpath(
            "//div[@class='article']"))
        self.parse_aside(book, response, response.xpath(
            "//div[@class='aside']"))
        return book

    def parse_article(self, book, response, article_content):
        """help parse article div part of the page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        self.parse_info(
            book, response, article_content.xpath("//div[@id='info']"))
        self.parse_interest(book, response, article_content.xpath(
            "//div[@id='interest_sectl']"))
        book["image_id"] = article_content.xpath(
            "//div[@id='mainpic']/a/@href").extract()[0]
        book["image_id"] = book["image_id"].split("/")[-1][1:-4]
        self.parse_related_info(
            book, response, article_content.xpath("div[@class='related_info']"))

    def parse_aside(self, book, response, aside_content):
        """help parse aside div part of the page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        self.parse_buyinfo(book, response, aside_content)
        self.parse_borrow_list(book, response, aside_content)
        self.parse_versions(book, response, aside_content)
        self.parse_in_doulist(book, response, aside_content)
        self.parse_num_read(book, response, aside_content)
        self.parse_secondhand_offer(book, response, aside_content)

    def parse_info(self, book, response, info_content):
        """help parse info div in the page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        book["authors"] = info_content.xpath(
            "span/a/text()").extract()
        book["series_id"] = info_content.xpath("a/@href").extract()
        if len(book["series_id"]) == 0:
            book["series_id"] = -1
        else:
            book["series_id"] = int(book["series_id"][0].split("/")[-1])
            if not r.sismember("series:set", book["series_id"]):
                series_base_url = "http://book.douban.com/series/%d"
                r.sadd("series:set", book["series_id"])
                r.rpush("series:start_urls", series_base_url %
                        book["series_id"])
        label_list = info_content.xpath(
            "span[@class='pl']/text()").extract()
        label_list = [label.strip()
                      for label in label_list if label.strip() != u""]
        if u"丛书:" in label_list:
            label_list.remove(u"丛书:")
        data_list = info_content.xpath("text()").extract()
        data_list = [data.strip() for data in data_list if data.strip() != u""]
        assert(len(label_list) == len(data_list))
        for i in xrange(len(label_list)):
            book[info_trans[label_list[i]]] = data_list[i]
        book["translators"] = info_content.xpath(
            "span/a/text()").extract()

    def parse_interest(self, book, response, interest_content):
        """help parse interest_sectl div part of the page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        if interest_content.xpath("//span[@class='color_gray']").extract() ==\
                [u"目前无人评价"]:
            book["rate_num"] = 0
            book["rate_score"] = 0
        else:
            if interest_content.xpath(
                "//div[@class='rating_sum']/span/a[@href='collections']/text()"
            ).extract()[0].strip() == u"评价人数不足":
                book["rate_num"] = 0
                book["rate_score"] = 0
            else:
                book["rate_num"] = int(interest_content.xpath(
                    '//span[@property="v:votes"]/text()'
                ).extract()[0].strip())
                book["rate_score"] = float(
                    interest_content.xpath(
                        '//strong/text()'
                    ).extract()[0].strip()
                )
            if not r.sismember("collections:set", book["book_id"]):
                r.sadd("collections:set", book["book_id"])
                r.rpush("collections:start_urls", response.url + "/collections")
        book["rate_star"] = interest_content.xpath(
            '//span[@class="rating_per"]/text()'
        ).extract()
        book["rate_star"] = [float(per[:-1]) for per in book["rate_star"]]

    def parse_related_info(self, book, response, related_content):
        """help parse related_info div part of the page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        self.parse_intro(book, response, related_content)
        self.parse_author_intro(book, response, related_content)
        self.parse_content(book, response, related_content)
        self.parse_tags(book, response, related_content)
        self.parse_comments(book, response, related_content)
        self.parse_reviews(book, response, related_content)
        self.parse_annotation(book, response, related_content)
        self.parse_discussion(book, response, related_content)

    def parse_intro(self, book, response, intro_content):
        """help parse intro part of page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        intro = intro_content.xpath(
            "//div[@class='indent' and @id='link-report']")
        temp = intro.xpath("//span[@class='all hidden']")
        if len(temp) != 0:
            intro = temp[0]
        book["intro"] = intro.xpath("//div[@class='intro']/p/text()").extract()

    def parse_author_intro(self, book, response, author_content):
        """help parse author_intro part of page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        author_intro = author_content.xpath("//div[@class='indent ']")
        temp = author_intro.xpath("//span[@class='all hidden ']")
        if len(temp) != 0:
            author_intro = temp[0]
        book["author_intro"] = author_intro.xpath(
            "//div[@class='intro']/p/text()").extract()

    def parse_content(self, book, response, content):
        """help parse content part of page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        c = content.xpath(
            '//div[@class="indent" and @id="dir_%d_full"]' % book["book_id"])
        if len(c) == 0:
            c = c.xpath(
                '//div[@class="indent" and @id="dir_%d_short"]' %
                book["book_id"])
        book["content"] = c.xpath("text()").extract()[:-2]

    def parse_tags(self, book, response, tags_content):
        """help parse tags part of page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        tags_num = tags_content.xpath(
            "//div[@id='db-tags-section']/h2/span/text()").extract()
        if len(tags_num) != 0:
            tags_num = tags_num[0]
        book["tags_num"] = number_re.search(tags_num).group(1)
        book["tags_list"] = tags_content.xpath(
            "//div[@class='indent']/span/a[@class='  tag']/text()").extract()

    def parse_user_like(self, book, response, userlike_content):
        """help parse user_like_also part of page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        book["user_like_also"] = userlike_content.xpath(
            "//div[@id='db-rec-section']/div/dl/dt/a/@href").extract()
        book["user_like_also"] = [url.split("/")[-2]
                                  for url in book["user_like_also"]]

    def parse_comments(self, book, response, comments_content):
        """help parse comments part of page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        comments_num = comments_content.xpath(
            "//div[@class='mod-hd']//span[@class='pl']/a/text()").extract()
        if len(comments_num) != 0:
            book["comments_num"] = int(
                number_re.search(comments_num[0]).group(1))
            if not r.sismember("collections:set", book["book_id"]):
                r.sadd("comments:set", book["book_id"])
                r.rpush("comments:start_urls", response.url + "/comments")
        else:
            book["comments_num"] = 0

    def parse_reviews(self, book, response, review_content):
        """help parse reviews in the page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        reviews_num = review_content.xpath(
            "//div[@id='reviews']//span[@class='pl']/a/" +
            "span[@property='v:count']/text()").extract()
        if len(reviews_num) != 0:
            book["reviews_num"] = int(reviews_num[0])
            if not r.sismember("reviews:set", book["book_id"]):
                r.sadd("reviews:set", book["book_id"])
                r.rpush("reviews:start_urls", response.url + "/reviews")
        else:
            book["reviews_num"] = 0

    def parse_annotation(self, book, response, annotation_content):
        """help parse annotation part of page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        annotations_num = annotation_content.xpath(
            '//div[@class="ugc-mod reading-notes"]//span[@class="pl"]/a/' +
            'span[@property="v:count"]/text()'
        ).extract()
        if len(annotations_num) != 0:
            book["annotations_num"] = int(annotations_num[0])
            if not r.sismember("annotations:set", book["book_id"]):
                r.sadd("annotations:set", book["book_id"])
                r.rpush("annotations:start_url", response.url + "/annotations")
        else:
            book["annotations_num"] = 0

    def parse_discussion(self, book, response, discussion_content):
        """help parse discussion part of page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        has_discussion = discussion_content.xpath(
            "//*[@id='db-discussion-section']/p/a").extract()
        if len(has_discussion) != 0:
            book["has_discussion"] = True
            if not r.sismember("discussion:set", book["book_id"]):
                r.sadd("discussion:set", book["book_id"])
                r.rpush("discussion:start_urls", response.url + "/annotations")
        else:
            book["has_discussion"] = False

    def parse_buyinfo(self, book, response, buyinfo_content):
        """help parse buyinfo div part of page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        if len(buyinfo_content.xpath("div[@id='buyinfo-printed']")) != 0:
            if not r.sismember("buyinfo:set", book["book_id"]):
                r.sadd("buyinfo:set", book["book_id"])
                r.rpush("buyinfo:start_urls", response.url + "/buylinks")

    def parse_borrow_list(self, book, response, borrow_content):
        """help parse borrow_list div part of page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        book["borrow_list"] = borrow_content.xpath(
            "div[@id='borrowinfo']/ul/li/a/text()").extract()

    def parse_versions(self, book, response, version_content):
        """TODO: Docstring for parse_versions.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        versions = version_content.xpath(
            "h2/span[@class='pl']/a[contains(@href, 'works')]")
        if len(versions) != 0:
            book["works_id"] = int(number_re.search(
                versions.xpath("@href").extract()[0]).group(1))
            if not r.sismember("works:set", book["works_id"]):
                works_base_url = "http://book.douban.com/works/%d"
                r.sadd("works:set", book["works_id"])
                r.rpush("works:start_urls", works_base_url % book["works_id"])
        else:
            book["works_id"] = -1

    def parse_in_doulist(self, book, response, doulist_content):
        """help parse in_doulist in the page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        doulist = doulist_content.xpath(
            "h2/span[@class='pl']/a[contains(@href, 'doulist')]")
        if len(doulist) != 0:
            book["in_doulist"] = True
            if not r.sismember("book_doulists:set", book["book_id"]):
                r.sadd("book_doulists:set", book["book_id"])
                r.rpush("book_doulists:start_urls", response.url + "/doulists")
        else:
            book["in_doulist"] = False

    def parse_num_read(self, book, response, numread_content):
        """help parse num_read part in the page.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        num_read = numread_content.xpath(
            "div[@id='collector']/p/a/text()").extract()
        if len(num_read) == 3:
            book["num_reading"] = int(number_re.search(num_read[0]).group(1))
            book["num_read"] = int(number_re.search(num_read[1]).group(1))
            book["num_want_read"] = int(number_re.search(num_read[2]).group(1))
            if book["num_reading"] > 0:
                if not r.sismember("doings:set", book["book_id"]):
                    r.sadd("doings:set", book["book_id"])
                    r.rpush("doings:start_urls", response.url + "/doings")
            if book["num_want_read"] > 0:
                if not r.sismember("wishes:set", book["book_id"]):
                    r.sadd("wishes:set", book["book_id"])
                    r.rpush("wishes:start_urls", response.url + "/wishes")
        else:
            book["num_reading"] = 0
            book["num_read"] = 0
            book["num_want_read"] = 0

    def parse_secondhand_offer(self, book, response, secondhand_content):
        """help parse second hand section.

        :book: TODO
        :response: TODO
        :returns: TODO

        """
        offers = secondhand_content.xpath(
            "//div[@class='indent' and not(@id)]" +
            "//ul[@class='bs']/li/a[@class=' ']")
        if len(offers) > 0:
            book["num_second_hand"] = int(
                number_re.search(offers.xpath("text()").extract()[0]).group(1))
            if not r.sismember("offers:set", book["book_id"]):
                r.sadd("offers:set", book["book_id"])
                r.rpush("offers:start_urls", response.url + "/offers")
