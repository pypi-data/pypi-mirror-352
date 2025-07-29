#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# JiuZero  2025/3/25

from lib.core.data import conf, KB
from lib.core.log import logger, colors
from lib.core.db import insertdb, selectdb
from data.rule.wafsignatures import rules
import requests, random, string, difflib, re
from urllib.parse import quote

def detector(self):
    KB.limit = True

    where = "HOSTNAME='{}'".format(self.requests.hostname)
    history1 = selectdb("WAFHISTORY", "WAFNAME", where=where)
    where = "HOSTNAME='{}'".format(self.requests.hostname)
    history2 = selectdb("CACHE", "HOSTNAME", where=where)
    
    # 存在WAF且本次启动后有检测过
    if history1 and history2:
        self.fingerprints.waf = str(history1[0])
        return
    # 不存在WAF且本次启动后有检测过
    elif not history1 and history2:
        self.fingerprints.waf = None
        return
    # 存在WAF但本次启动后没有检测过
    elif history1 and not history2:
        if conf.skip_waf_recheck:
            self.fingerprints.waf = str(history1[0])
            return
    # 不存在WAF但本次启动后没有检测（未知情况）
    # 尝试指纹匹配
    # Reference: https://github.com/al0ne/Vxscan
    for i in rules:
        name, position, regex = i.split('|')
        if position == "text":
            if re.search(regex, str(self.requests.raw)):
                logger.warning("<{}{}{}> Protected by {}".format(colors.m, self.requests.hostname, colors.e, name))
                self.fingerprints.waf = name
                return
        else:
            if self.requests.headers is not None:
                headers = {k.lower(): v for k, v in self.requests.headers.items()}
                if headers.get(position):
                    if re.search(regex, headers.get(position).lower()) is not None:
                        logger.warning("<{}{}{}> Protected by {}".format(colors.m, self.requests.hostname, colors.e, name))
                        self.fingerprints.waf = name
                        return
    rand_param = '/?' + ''.join(random.choices(string.ascii_lowercase, k=4)) + '='
    payload = "UNION ALL SELECT 1,'<script>alert(\"XSS\")</script>' FROM information_schema WHERE --/**/ EXEC xp_cmdshell('cat ../../../etc/passwd')#"
    try:
        r1 = requests.get(self.requests.netloc)
        r2 = requests.get(self.requests.netloc + rand_param + quote(payload))
    # 超时与连接问题很可能产生于WAF
    except (TimeoutError, ConnectionError, Exception) as e:
        deal(self, True)
        return
    # 页面相似度判断
    similarity = difflib.SequenceMatcher(r1.text, r2.text).ratio()
    if similarity < 0.5:
        deal(self, True)
        return
    else:
        print(2)
        deal(self, False)


def deal(self, state):
    if state:
        logger.warning("<{}{}{}> Protected by some kind of WAF/IPS".format(colors.m, self.requests.hostname, colors.e))
        self.fingerprints.waf = "UNKNOW"
        cv = {"HOSTNAME": self.requests.hostname,
              "WAFNAME": "UNKNOW"}
        insertdb("WAFHISTORY", cv)
        return
    else:
        self.fingerprints.waf = None
        return