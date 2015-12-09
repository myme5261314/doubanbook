#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 Peng Liu <liupeng@imscv.com>
#
# Distributed under terms of the GNU GPL3 license.

"""
This is the abstract class for the proxy server info gather.
"""


class BaseProxyGenerator(object):

    """Define Some data variables and common operations for various kinds of
    proxy generators."""

    def __init__(self, url):
        """Initialize the common data variables.
        :url: this is the link to gather information of proxies.

        """
        self.base_url = url

    def gather(self):
        """Convert the gathered data and stored in the instance.
        :returns: dict of (hash, BaseProxy) pair.

        """
        pass

    def _extract(self):
        """TODO: extract info based on specific website structure and url.

        :returns: List of BaseProxy.

        """
        return []

    def _check(self, proxy_list):
        """TODO: Check each of the the BaseProxy whether they are available.

        :proxy_list: the input list from gather webpage.
        :returns: the checked list of proxies.

        """
        pass
