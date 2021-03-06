# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DoubanbookItem(scrapy.Item):
    book_id = scrapy.Field()
    title = scrapy.Field()
    # ['作者', '出版社:', '出版年:', '页数:', '定价:', '装帧:', 'ISBN:',
    # '副标题:', '译者', '丛书:', '原作名:']
    authors = scrapy.Field()
    press = scrapy.Field()
    year = scrapy.Field()
    pages = scrapy.Field()
    price = scrapy.Field()
    binding = scrapy.Field()
    isbn = scrapy.Field()
    csbn = scrapy.Field()
    subtitle = scrapy.Field()
    translators = scrapy.Field()
    series_id = scrapy.Field()
    origin_name = scrapy.Field()

    image_id = scrapy.Field()
    # limage = scrapy.Field()
    # simage = scrapy.Field()

    rate_num = scrapy.Field()
    rate_score = scrapy.Field()
    rate_star = scrapy.Field()

    intro = scrapy.Field()
    author_intro = scrapy.Field()
    content = scrapy.Field()
    tags_num = scrapy.Field()
    tags_list = scrapy.Field()

    user_like_also = scrapy.Field()

    comments_num = scrapy.Field()
    reviews_num = scrapy.Field()
    annotations_num = scrapy.Field()

    has_discussion = scrapy.Field()

    borrow_list = scrapy.Field()

    works_id = scrapy.Field()

    in_doulist = scrapy.Field()

    num_reading = scrapy.Field()
    num_read = scrapy.Field()
    num_want_read = scrapy.Field()

    num_second_hand = scrapy.Field()


class SeriesItem(scrapy.Item):
    series_id = scrapy.Field()
    series_name = scrapy.Field()
    book_num = scrapy.Field()
    book_list = scrapy.Field()
    recommend_num = scrapy.Field()
    contribute_list = scrapy.Field()


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
