#! /bin/sh
#
# sitemap_downloader.sh
# Copyright (C) 2015 Peng Liu <liupeng@imscv.com>
#
# Distributed under terms of the GNU GPL3 license.
#


for i in {1..3345}
do
    axel http://www.douban.com/sitemap${i}.xml.gz
done
