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
    if suffix == ".jsp" or suffix == ".do" or suffix == ".action":
        return "JAVA", None
    if 'set-cookie' in headers.keys():
        if search(r"JSESSIONID", headers["set-cookie"], I):
            return "JAVA", None
    for item in headers.items():
        if search(r'Java|Servlet|JSP|JBoss|Glassfish|Oracle|JRE|JDK|JSESSIONID', str(item)):
            return "JAVA", None
        elif search(r'\.jsp$|\.jspx$|.do$|\.wss$|\.action$', content):
            return "JAVA", None
    return None, None
