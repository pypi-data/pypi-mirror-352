#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# w8ay 2019/6/29
# JiuZero 2025/3/4

import copy
import requests
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor, as_completed
from lib.core.common import get_middle_text, generateResponse
from api import conf, HTTPMETHOD, PLACE, VulType, Type, PluginBase, logger


class Z0SCAN(PluginBase):
    name = "sensi-php-realpath"
    desc = 'Php Real Path Finder'
    version = "2025.3.4"
    risk = 0
        
    def audit(self):
        if conf.level == 0 or not 0 in conf.risk or conf.level == 0:
            return
        if self.fingerprints.programing.get("PHP", False):
            headers = deepcopy(self.requests.headers)
            iterdatas = self.generateItemdatas()
            with ThreadPoolExecutor(max_workers=None) as executor:
                futures = [
                    executor.submit(self.process, _) for _ in iterdatas
                ]
                try:
                    for future in as_completed(futures):
                        try:
                            future.result()
                        except Exception as task_e:
                            logger.error(f"Task failed: {task_e}", origin=self.name)
                except KeyboardInterrupt:
                    executor.shutdown(wait=False)
                except Exception as e:
                    logger.error(f"Unexpected error: {e}", origin=self.name)
                    executor.shutdown(wait=False)
                    
    def process(self, _):
        k, v, position = _
        _k = k + "[]"
        payload = self.insertPayload({
            "key": _k, 
            "value": v, 
            "position": position,
            })
        r = self.req(position, payload)
        if "Warning" in r.text and "array given in " in r.text:
            path = get_middle_text(r.text, 'array given in ', ' on line')
            result = self.generate_result()
            result.main({
                "type": Type.REQUEST, 
                "url": self.requests.url, 
                "vultype": VulType.SENSITIVE, 
                "show": {
                    "Position": position, 
                    "Msg": "{}".format(path), 
                    "Param": _k
                    }
                })
            result.step("Request1", {
                "request": r.reqinfo, 
                "response": generateResponse(r), 
                "desc": "{}".format(path)
                })
            self.success(result)
            return
