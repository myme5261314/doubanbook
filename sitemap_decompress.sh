#! /bin/sh
#
# sitemap_decompress.sh
# Copyright (C) 2015 Peng Liu <liupeng@imscv.com>
#
# Distributed under terms of the GNU GPL3 license.
#


for i in {1..3345}
do
    gunzip sitemap/sitemap${i}.xml.gz > sitemap${i}.xml
done
