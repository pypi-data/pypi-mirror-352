#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# w8ay 2019/7/11
# JiuZero 2025/3/4

import requests

from api import generateResponse, conf, VulType, PLACE, PluginBase, Type, KB
from lib.helper.helper_phpinfo import get_phpinfo


class Z0SCAN(PluginBase):
    name = "sensi-php-phpinfo"
    desc = 'Phpinfo Finder'
    version = "2025.3.4"
    risk = 0
    
    def audit(self):
        if self.fingerprints.programing.get("PHP", False) and 0 in conf.risk and conf.level != 0:
            headers = self.requests.headers.copy()
            for phpinfo in KB.dicts["phpinfo"]:
                testURL = self.requests.netloc.rstrip("/") + "/" + phpinfo
                r = requests.get(testURL, headers=headers)
                if "<title>phpinfo()" in r.text or "php_version" in r.text:
                    info = get_phpinfo(r.text)
                    result = self.generate_result()
                    result.main({
                        "type": Type.REQUEST, 
                        "url": r.url, 
                        "vultype": VulType.SENSITIVE
                        })
                    result.step("Request1", {
                        "request": r.reqinfo, 
                        "response": generateResponse(r), 
                        "desc": ''.join(info)
                        })
                    self.success(result)
