#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# w8ay 2019/7/4
# JiuZero 2025/5/15

import random
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from api import VulType, md5, generateResponse, conf, PluginBase, Type, logger
from lib.helper.helper_sensitive import sensitive_page_error_message_check


class Z0SCAN(PluginBase):
    name = "codei-php"
    desc = 'PHP Code Injection'
    version = "2025.5.15"
    risk = 3
            
    def audit(self):
        if conf.level == 0 or not 3 in conf.risk:
            return
        if self.fingerprints.programing.get("PHP", False) and not self.fingerprints.waf:
            regx = r'Parse error: syntax error,.*?\sin\s'
            randint = random.randint(5120, 10240)
            verify_result = md5(str(randint).encode())
            _payloads = [
                r"print(md5({}));".format(randint),
                r";print(md5({}));".format(randint),
                r"';print(md5({}));$a='".format(randint),
                r"\";print(md5({}));$a=\"".format(randint),
                r"${{@print(md5({}))}}".format(randint),
                r"${{@print(md5({}))}}\\".format(randint),
                r"'.print(md5({})).'".format(randint)
            ]

            iterdatas = self.generateItemdatas()
            with ThreadPoolExecutor(max_workers=None) as executor:
                futures = [
                    executor.submit(self.process, _, _payloads, verify_result, regx) for _ in iterdatas
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

    def process(self, _, position, _payloads, verify_result, regx):
        k, v, position = _
        errors = None
        errors_raw = ()
        for _payload in _payloads:
            payload = self.insertPayload({
                "key": k, 
                "position": position, 
                "payload": _payload
                })
            r = self.req(k, v, position, payload)
            if not r:
                continue
            html1 = r.text
            if verify_result in html1:
                result = self.generate_result()
                result.main({
                    "type": Type.REQUEST, 
                    "url": self.requests.url, 
                    "vultype": VulType.SENSITIVE, 
                    "show": {
                        "Position": position, 
                        "Param": key, 
                        "Payload": value
                        }
                    })
                result.step("Request1", {
                    "request": r.reqinfo, 
                    "response": generateResponse(r), 
                    "desc": "Receive {}".format(verify_result)
                    })
                self.success(result)
                break
            if re.search(regx, html1, re.I | re.S | re.M):
                result = self.generate_result()
                result.main({
                    "type": Type.REQUEST, 
                    "url": self.requests.url, 
                    "vultype": VulType.SENSITIVE, 
                    "show": {
                        "Position": position, 
                        "Param": key, 
                        "Payload": value
                        }
                    })
                result.step("Request1", {
                    "request": r.reqinfo, 
                    "response": generateResponse(r), 
                    "desc": "Receive Return {}, maybe is the error because of payload".format(regx)
                    })
                self.success(result)
                break
            if not errors:
                errors = sensitive_page_error_message_check(html1)
                if errors:
                    errors_raw = (k, v)

        if errors:
            result = self.generate_result()
            key, value = errors_raw
            result.main({
                "type": Type.REQUEST, 
                "url": self.requests.url, 
                "vultype": VulType.SENSITIVE, 
                "show": {
                    "Position": position, 
                    "Param": key, 
                    "Payload": value
                    }
                })
            for m in errors:
                text = m["text"]
                _type = m["type"]
                result.step("Request1", {
                    "request": r.reqinfo, 
                    "response": generateResponse(r), 
                    "desc": "Match Tools:{} Match:{}".format(_type, text)
                    })
            self.success(result)
