#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 Peng Liu <liupeng@imscv.com>
#
# Distributed under terms of the GNU GPL3 license.

"""
This is some utility functions related to string.
"""


def filter_zhcn(s):
    """This function will remove all the non-English words in the string.

    :s: input string.
    :returns: output string that only contains English charset.

    """
    char_ords = map(ord, s)
    return ''.join([s[idx] for idx in xrange(len(s)) if char_ords <= 127])
