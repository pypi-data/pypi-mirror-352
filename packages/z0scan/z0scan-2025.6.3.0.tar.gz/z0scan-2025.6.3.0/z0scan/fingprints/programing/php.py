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
    if suffix == ".php" or suffix == ".phtml":
        return "PHP", None
    if _prepare_pattern(r"\.php(?:$|\?)").search(content):
        return "PHP", None
    if 'server' in headers.keys():
        if search(r"php/?([\d.]+)?\;version:\1", headers["server"], I):
            return "PHP", None
    if 'set-cookie' in headers.keys():
        if search(r"PHPSESSID", headers["set-cookie"], I):
            return "PHP", None
    if 'x-powered-by' in headers.keys():
        if search(r"php/?([\d.]+)?\;version:\1", headers["x-powered-by"], I):
            return "PHP", None
    return None, None