#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Reference: https://github.com/shenril/Sitadel
# JiuZero 2025/5/12

import re
import requests
from api import generateResponse, VulType, PLACE, HTTPMETHOD, PluginBase, conf, KB, Type

class Z0SCAN(PluginBase):
    name = "other-xst"
    desc = 'XST'
    version = "2025.5.12"
    risk = -1
    
    def audit(self):
        if not conf.level == 0 and -1 in conf.risk:
            r = requests.request("TRACE", self.requests.netloc + "/*", allow_redirects=True, verify=False, headers={"Z0SCAN": "z0scanXST"})
            if re.search("Z0SCAN: *?z0scanXST", r.text, re.I):
                result = self.generate_result()
                result.main({
                    "type": Type.REQUEST, 
                    "url": self.requests.url, 
                    "vultype": VulType.SENSITIVE
                    })
                result.step("Request1", {
                    "request": r.reqinfo, 
                    "response": generateResponse(r), 
                    "desc": "Status Code is 204"
                    })
                self.success(result)