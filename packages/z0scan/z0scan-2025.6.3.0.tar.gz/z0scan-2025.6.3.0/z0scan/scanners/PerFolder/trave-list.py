#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# JiuZero 2025/5/11

import re, requests
from api import VulType, PLACE, PluginBase, Type, conf, generateResponse


class Z0SCAN(PluginBase):
    name = "trave-list"
    desc = "List"
    version = "2025.5.11"
    risk = 2

    def audit(self):
        if not 2 in conf.risk or conf.level == 0:
            return
        resp_str = self.response.text
        flag_list = [
            "directory listing for",
            "<title>directory",
            "<head><title>index of",
            '<table summary="directory listing"',
            'last modified</a>',
        ]
        for i in flag_list:
            if i in resp_str.lower():
                result = self.generate_result()
                result.main({
                    "type": Type.ANALYZE,
                    "url": self.requests.url, 
                    "vultype": VulType.SENSITIVE
                    })
                result.step("Request1", {
                    "request": self.requests.raw, 
                    "response": self.response.raw, 
                    "desc": "{}".format(i)
                    })
                self.success(result)
                return
        # Vulscan
        match = re.search(r"<title>(.*?)</title>", resp_str.lower(), re.DOTALL)
        if not match:
            return
        title = match.group(1)
        if "index of" in title or "everything" in title:
            result = self.generate_result()
            result.main({
                "type": Type.ANALYZE,
                "url": self.requests.url, 
                "vultype": VulType.SENSITIVE
                })
            result.step("Request1", {
                "request": self.requests.raw, 
                "response": self.response.raw, 
                "desc": '"index of" in title or "everything" in title'
                })
            self.success(result)
            return
        if conf.level == 3:
            r = requests.request("GET", self.requests.netloc + "/.listing", allow_redirects=True, verify=False)
            # 判断写得有些草率…后面再改
            if r.status_code == 200:
                result = self.generate_result()
                result.main({
                    "type": Type.ANALYZE, 
                    "url": self.requests.netloc + "/.listing", 
                    "vultype": VulType.OTHER
                    })
                result.step("Request1", {
                    "request": r.reqinfo, 
                    "response": generateResponse(r), 
                    "desc": ""
                    })
                self.success(result)
        
