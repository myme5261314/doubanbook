#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 Peng Liu <liupeng@imscv.com>
#
# Distributed under terms of the GNU GPL3 license.

"""
This is the base class for the proxy server information.
"""

import requests as rs
from bs4 import BeautifulSoup as bs
import time


class BaseProxy(object):

    """Docstring for BaseProxy. """

    def __init__(self):
        """TODO: to be defined1. """
        self.data_dict = dict()
        # Make sure the 'hash' and 'usable' entries are always the first two
        # entry of the list.
        self.key_words = ['hash', 'usable', 'ip', 'port', 'anonymity',
                          'type_list', 'position', 'response_time',
                          'verify_time']
        self.data_dict[self.key_words[0]] = hash('-1')
        self.data_dict[self.key_words[1]] = True
        self.data_dict[self.key_words[2]] = ''
        self.data_dict[self.key_words[3]] = 0
        self.data_dict[self.key_words[4]] = ''
        self.data_dict[self.key_words[5]] = []
        self.data_dict[self.key_words[6]] = ''
        self.data_dict[self.key_words[7]] = 0.0
        self.data_dict[self.key_words[8]] = time.time()

    def convert(self, content_list):
        """Convert the gathered data and stored in the instance.
        :content_list: It contains the same order of base class initialization.
        :returns: True for success, False for fail.

        """
        for i in xrange(len(content_list)):
            self.data_dict[self.key_words[i]] = content_list[i]

    def check(self):
        """Check whether proxy server is usable.

        :returns: True for usable and False for unusable.

        """
        if self.data_dict['response_time'] > 3:
            self.data_dict['usable'] = False
            return False
        else:
            url = 'http://www.baidu.com'
            soup = bs(
                rs.get(url, timeout=3, proxies={
                    'http': 'http://%s:%d' % (self.data_dict['ip'],
                                              self.data_dict['port'])}).text,
                'html.parser')
            if soup.title.text != u'百度一下，你就知道':
                self.data_dict['usable'] = False
                return False
            else:
                self.data_dict['usable'] = True
                return True
