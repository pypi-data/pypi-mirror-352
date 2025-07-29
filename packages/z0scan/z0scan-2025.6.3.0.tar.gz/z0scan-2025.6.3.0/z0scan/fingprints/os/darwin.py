#!/usr/bin/env python 
# -*- coding:utf-8 -*-

from re import search, I, compile, error

def _prepare_pattern(pattern):
    """
    Strip out key:value pairs from the pattern and compile the regular
    expression.
    """
    regex, _, rest = pattern.partition(r'\;')
    try:
        return compile(regex, I)
    except error as e:
        return compile(r'(?!x)x')


def fingerprint(suffix, headers, content):
    if 'server' in headers.keys():
        if search(r"Darwin", headers["server"], I):
            return "DARWIN", None
    if 'x-powered-by' in headers.keys():
        if search(r"Darwin", headers["x-powered-by"], I):
            return "DARWIN", None
    return None, None
