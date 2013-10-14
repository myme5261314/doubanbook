#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2013-9-18

@author: peng
'''
#!/usr/bin/env python
# coding:utf-8
# reference https://groups.google.com/forum/#!topic/qunpin/kkdZ4iIQgbc
import json
import urllib
import threading
import time
import sys
import MySQLdb
import datetime

print sys.getdefaultencoding()
start_id = 5000001
end_id = 10000000
grabbing = True
lock = threading.Lock()
conn = MySQLdb.connect(host='localhost', port=3306, user='root',
                       passwd='5261314', charset='utf8')
cur = conn.cursor()

cur.execute("SET NAMES utf8")
# cur.execute("SET CHARACTER_SET_CLIENT=utf8")
# cur.execute("SET CHARACTER_SET_DATABASE=utf8")
# cur.execute("SET CHARACTER_SET_SERVER=utf8")
# cur.execute("SET CHARACTER_SET_RESULTS=utf8")
conn.commit()

cur.execute('create database if not exists douban_book CHARACTER SET `utf8` \
COLLATE `utf8_general_ci`; ')
cur.execute('use douban_book')
tb = 'book_%s_%s' % (start_id, end_id)
cur.execute('''CREATE TABLE IF NOT EXISTS `%s` (
`id`  INT NOT NULL ,
`isbn10`  VARCHAR(10) ,
`isbn13`  VARCHAR(13) ,
`title`   VARCHAR(100) ,
`origin_title`  VARCHAR(100) ,
`alt_title`  VARCHAR(100) ,
`sub_title`  VARCHAR(100) ,
`url`  VARCHAR(100) ,
`alt`  VARCHAR(100) ,
`image`  VARCHAR(100) ,
`author`  VARCHAR(100) ,
`translator`  VARCHAR(100) ,
`publisher`  VARCHAR(100) ,
`pubdate`  VARCHAR(10) ,
`numRaters`  INT ,
`averageRate`  FLOAT ,
`tags`  TEXT ,
`binding`  VARCHAR(10) ,
`price`  VARCHAR(20) ,
`pages`  VARCHAR(10) ,
`author_info`  TEXT ,
`summary`  TEXT ,
`catalog`  TEXT ,
`addtime` DATETIME ,
PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;;
''' % tb
)

insert_template = '''insert into `%s` values(
%d,'%s','%s','%s','%s','%s','%s','%s','%s','%s',
'%s','%s','%s','%s',%d,%f,'%s','%s','%s','%s' ,
'%s','%s', '%s', '%s'
)'''

blocks = 200
blocks_write = 5*blocks
initial_blocks = 3*blocks_write
blocks_starttime = datetime.datetime.now()

cur.execute('select id from `%s` order by id desc limit 1' % tb)
top = cur.fetchone()
if top is not None and top > start_id:
    top = top[0]
    top = top - initial_blocks
    if top < start_id:
        top = start_id
    start_id = top

ranges = iter(xrange(start_id, end_id))
print top
print start_id

conn.autocommit(0)
initialed = False
timers = 0

class Book:
    def __init__(self, j):
        valid = lambda x, y: True if x.has_key(y) and x[y] != '' else False
        valid_list = lambda x, y: True if x.has_key(y) and x[y] != [] else False
        transform = lambda x: x.replace('\\', '\\\\').replace("\'", "\\'").replace("\"", "\\\"")
        getvalue_str = lambda x, y: transform(x[y]) if valid(x, y) else ''
        getvalue_int = lambda x, y: int(x[y]) if valid(x, y) else 0
        getvalue_float = lambda x, y: float(x[y]) if valid(x, y) else 0.0
        getvalue_list = lambda x, y: x[y] if valid_list(x, y) else []
        
        self.id = getvalue_int(j, 'id')
        self.isbn10 = getvalue_str(j, 'isbn10')
#         print self.id
        self.isbn13 = getvalue_int(j, 'isbn13')
        self.title = getvalue_str(j, 'title')
        self.origin_title = getvalue_str(j, 'origin_title')
        self.alt_title = getvalue_str(j, 'alt_title')
        self.subtitle = getvalue_str(j, 'subtitle')
        self.url = getvalue_str(j, 'url')
        self.alt = getvalue_str(j, 'alt')
        if j['image'] == "http:\/\/img3.douban.com\/pics\/book-default-medium.gif":
            self.image = 'default'
#             self.images = 'default'
        else:
            self.image = getvalue_str(j, 'image')
#             self.s_image = j['images']['small']
#             self.m_image = j['images']['medium']
#             self.l_image = j['images']['large']
        author_list = getvalue_list(j, 'author')
        self.author = ''
        for author in author_list:
            self.author += '%s|' % transform(author)
        if self.author != '':
            self.author = self.author[:-1]
        translator_list = getvalue_list(j, 'translator')
        self.translator = ''
        for translator in translator_list:
            self.translator += '%s|' % transform(translator)
        if self.translator != '':
            self.translator = self.translator[:-1]
        self.publisher = getvalue_str(j, 'publisher')
        self.pubdate = getvalue_str(j, 'pubdate')
        self.numRaters = getvalue_int(j['rating'], 'numRaters')
        self.averageRate = getvalue_float(j['rating'], 'average')
        self.tags = ''
        taglist = getvalue_list(j, 'tags')
        for tag in taglist:
            self.tags += '%s:%s|' % (transform(tag['name']), tag['count'])
        if self.tags != '':
            self.tags = self.tags[:-1]
        self.binding = getvalue_str(j, 'binding')
        self.price = getvalue_str(j, 'price')
        self.pages = getvalue_str(j, 'pages')
        self.author_intro = getvalue_str(j, 'author_intro')
        self.summary = getvalue_str(j, 'summary')
        self.catalog = getvalue_str(j, 'catalog')
        
        self.need_fetch = False
# 
#     def __getattr__(self, item):
#         return self[item]



# max = 19973896
class Douban(threading.Thread):
    def __init__(self, id):
        super(Douban, self).__init__()

        self.id = id

    def getImg(self, url):
        return urllib.urlopen(url).read()

    def run(self):
        url = 'https://api.douban.com/v2/book/%s' % self.id
        try:
            jsn = urllib.urlopen(url).read()
            meta = json.loads(jsn)
            if not meta.has_key('code'):
#                 jsn = jsn.replace("'", "\\'")
                book = Book(meta)
                lock.acquire()
                sql = insert_template % (tb,
                     self.id, book.isbn10, book.isbn13,
                     book.title, book.origin_title, book.alt_title, book.subtitle,
                     book.url, book.alt, book.image,
                     book.author, book.translator, book.publisher, book.pubdate,
                     book.numRaters, book.averageRate, book.tags,
                     book.binding, book.price, book.pages,
                     book.author_intro, book.summary, book.catalog,
                     datetime.datetime.now()
                     )
                try:
                    global initialed, timers, initial_blocks, blocks_write, blocks_starttime
                    if not initialed:
                        if timers != 0 and timers % initial_blocks == 0:
                            timers = 0
                            initialed = True
                            print 'Initialed Time:', datetime.datetime.now() - blocks_starttime
                            blocks_starttime = datetime.datetime.now()
                        else:
                            timers += 1
                        cur.execute(sql)
                        conn.commit()
                    else:
#                         timers += 1
                        cur.execute(sql)
                        if timers != 0 and timers % blocks_write == 0:
                            timers = 0
                            conn.commit()
                            print '----------------------------------commit %d records---------------------------' % timers
                            print 'blocks time:', datetime.datetime.now() - blocks_starttime
                            blocks_starttime = datetime.datetime.now()
                        else:
                            timers += 1
#                     cur.execute(sql)
                    print datetime.datetime.now()
                    global timers
                    print self.id, 'ok', timers
                except Exception as e:
#                     print self.id, 'already grabbed'
                    print self.id, e
                lock.release()
            else:
                print self.id, meta['msg']
        except Exception as e:
            print self.id, e
        try:
            grab(ranges.next())
        except StopIteration:
            global grabbing
            grabbing = False
            print 'over'


def grab(id):
    task = Douban(id)
    task.setDaemon(True)
    task.start()


def main():
    # 6???
    
    for i in range(blocks):
        grab(ranges.next())
    while grabbing:
        time.sleep(0.001)


if __name__ == '__main__':
    main()