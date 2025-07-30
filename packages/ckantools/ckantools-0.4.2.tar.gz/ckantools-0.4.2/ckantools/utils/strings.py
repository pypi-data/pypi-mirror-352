# !/usr/bin/env python
# encoding: utf-8

import re


def split_caps(string_input):
    """
    Adds spaces around capital letters.
    """
    return re.sub('(.)(?=[A-Z][^A-Z])', '\\1 ', string_input)
