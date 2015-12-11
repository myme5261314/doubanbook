# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DoubanbookItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    book_id = scrapy.Field()
    title = scrapy.Field()
    subtitle = scrapy.Field()
    author = scrapy.Field()
    press = scrapy.Field()
    year = scrapy.Field()
    month = scrapy.Field()
    pages = scrapy.Field()
    price = scrapy.Field()
    binding = scrapy.Field()
    isbn = scrapy.Field()
    cover = scrapy.Field()
    series_id = scrapy.Field()

    introduction = scrapy.Field()
    content = scrapy.Field()
    tags = scrapy.Field()


class CommentItem(scrapy.Item):
    # Use this item to sotre one comment entry to certain book.
    comment_id = scrapy.Field()


class ReviewItem(scrapy.Item):
    # Use this item to sotre one comment entry to certain book.
    review_id = scrapy.Field()


class AnnotationItem(scrapy.Item):
    # Use this item to sotre one comment entry to certain book.
    annotation_id = scrapy.Field()


class Disscussion(scrapy.Item):
    # Use this item to sotre one comment entry to certain book.
    discussion_id = scrapy.Field()


class ProxyServerItem(scrapy.Item):
    # Use this item to process proxy server information.
    index = scrapy.Field()
    ip = scrapy.Field()
    port = scrapy.Field()
    status = scrapy.Field()
    response_time = scrapy.Field()
    verify_time = scrapy.Field()