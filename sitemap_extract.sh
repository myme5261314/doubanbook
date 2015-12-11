#! /bin/sh
#
# sitemap_extract.sh
# Copyright (C) 2015 Peng Liu <liupeng@imscv.com>
#
# Distributed under terms of the GNU GPL3 license.
#


grep -o 'http://book.douban.com/subject/[0-9]*/' sitemap/sitemap*.xml | sed 's/[^0-9]//g' > bookid.txt
