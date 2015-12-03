#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 Peng Liu <liupeng@imscv.com>
#
# Distributed under terms of the GNU GPL3 license.

"""
This file contains utility functions about proxy server.
"""

import requests as rs
from bs4 import BeautifulSoup as bs
from class_type import ProxyServer

base_url = 'http://www.kuaidaili.com/proxylist/'


def get_proxy_list():
    """Get a list of current proxies from the web.
    :returns: a list of ProxyServer instances.

    """
    proxies = []
    for i in xrange(10):
        proxy_url = '%s%d' % (base_url, i)
        soup = bs(rs.get(proxy_url).text, 'html.parser')
        for entry in soup.find_all(['tr'])[1:]:
            info_list = entry.find_all(['td'])
            info_list = [info.text for info in info_list]
            data_dict = dict()
            data_dict['ip'] = info_list[0]
            data_dict['port'] = info_list[1]
            data_dict['anonymity'] = info_list[2]
            data_dict['types'] = info_list[3]
            data_dict['get_post'] = info_list[4]
            data_dict['position'] = info_list[5]
            data_dict['response_time'] = info_list[6]
            data_dict['verify_time'] = info_list[7]
            proxies.append(ProxyServer.ProxyServer(data_dict))
    return proxies


def main():
    """TODO: Docstring for main.
    :returns: TODO

    """
    print map(str, get_proxy_list())

if __name__ == "__main__":
    main()
