#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 Peng Liu <liupeng@imscv.com>
#
# Distributed under terms of the GNU GPL3 license.

"""
This is the class file for the type of ProxyServer which is fetched from
http://www.kuaidaili.com/
"""

import time


class ProxyServer(object):
    """This class is just place to hold some proxy server information."""

    def __init__(self, data_dict):
        super(ProxyServer, self).__init__()
        self.ip = data_dict['ip']
        self.port = int(data_dict['port'])
        self.anonymity = data_dict['anonymity']
        self.types = data_dict['types'].strip(' ').split(',')
        self.get_post = data_dict['get_post'].strip(' ').split(',')
        self.position = data_dict['position']
        self.response_time = float(data_dict['response_time'][:-1])
        self.verify_time = time.time() - 60 * int(data_dict['verify_time'][:-3])

        self.failed_times = 0

    def __hash__(self):
        return hash(self.__str__())

    def __eq__(self, other):
        return other and isinstance(
            other, type(ProxyServer)) and self.__hash__() == other.__hash__()

    def __gt__(self, other):
        assert(isinstance(other, type(ProxyServer)))
        return self.__float__() > other.__float__()

    def __str__(self):
        return 'http://' + self.ip + ':' + str(self.port)

    def __repr__(self):
        return self.__str__()

    def __float__(self):
        return self.response_time + 1.0/self.verify_time

    def fail(self):
        """Involke when the proxy server request failed a time.

        :returns: TODO

        """
        self.failed_times += 1

    def need_terminate(self, threshold_times=100):
        """Determine terminate or not with threshold_times.

        :threshold_times: the max failed times that can tolerant.
        :returns: True for terminate, False for not.

        """
        return self.failed_times >= threshold_times
