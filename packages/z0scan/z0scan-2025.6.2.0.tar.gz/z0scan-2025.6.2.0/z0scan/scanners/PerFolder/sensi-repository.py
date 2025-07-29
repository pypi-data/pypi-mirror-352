#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# w8ay 2019/6/29
# JiuZero 2025/3/4

import re
import requests

from api import KB, conf, generateResponse, VulType, PLACE, PluginBase, Type


class Z0SCAN(PluginBase):
    name = "sensi-repository"
    desc = '.git .svn .bzr .hg Finder'
    version = "2025.3.4"
    risk = 1
    
    def audit(self):
        if not self.fingerprints.waf and 1 in conf.risk and conf.level != 0:
            flag = {
                "/.svn/all-wcprops": r"svn:wc:ra_dav:version-url",
                "/.git/config": r'repositoryformatversion[\s\S]*',
                "/.bzr/README": r'This\sis\sa\sBazaar[\s\S]',
                '/CVS/Root': r':pserver:[\s\S]*?:[\s\S]*',
                '/.hg/requires': r'^revlogv1.*'
            }
            headers = self.requests.headers.copy()
            for f in flag.keys():
                _ = self.requests.url.rstrip('/') + f
                r = requests.get(_, headers=headers)
                if re.search(flag[f], r.text, re.I | re.S | re.M):
                    result = self.generate_result()
                    result.main({
                        "type": Type.REQUEST, 
                        "url": r.url, 
                        "vultype": VulType.SENSITIVE
                        })
                    result.step("Request1", {
                        "request": r.reqinfo, 
                        "response": generateResponse(r), 
                        "desc": "{}".format(flag[f])
                        })
                    self.success(result)
