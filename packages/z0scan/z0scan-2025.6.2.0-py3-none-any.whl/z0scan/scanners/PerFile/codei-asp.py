#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# w8ay 2019/7/4
# JiuZero 2025/5/15

import random
from concurrent.futures import ThreadPoolExecutor, as_completed

from api import PluginBase, conf, VulType, generateResponse, Type, logger


class Z0SCAN(PluginBase):
    name = "codei-asp"
    desc = 'ASP Code Injection'
    version = "2025.5.15"
    risk = 3
        
    def audit(self):
        if conf.level == 0 or not 3 in conf.risk:
            return
        if self.fingerprints.programing.get("PHP", False) and not self.fingerprints.waf:
            randint1 = random.randint(10000, 90000)
            randint2 = random.randint(10000, 90000)
            randint3 = randint1 * randint2
            _payloads = [
                'response.write({}*{})'.format(randint1, randint2),
                '\'+response.write({}*{})+\''.format(randint1, randint2),
                '"response.write({}*{})+"'.format(randint1, randint2),
            ]
            
            iterdatas = self.generateItemdatas()
            with ThreadPoolExecutor(max_workers=None) as executor:
                futures = [
                    executor.submit(self.process, _, _payloads, randint3) for _ in iterdatas
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
                    
    def process(self, _, _payloads, randint3):
        k, v, position = _
        for _payload in _payloads:
            payload = self.insertPayload({
                "key": k,
                "payload": _payload, 
                "position": position, 
                })
            r = self.req(position, payload)
            if not r:
                continue
            html = r.text
            if str(randint3) in html:
                result = self.generate_result()
                result.main({
                    "type": Type.REQUEST, 
                    "url": r.url, 
                    "vultype": VulType.CODE_INNJECTION, 
                    "show": {
                        "Position": position, 
                        "Param": k, 
                        "payload": payload, 
                        }
                    })
                result.step("Request1", {
                    "request": r.reqinfo, 
                    "response": generateResponse(r), 
                    "desc": "Match Int {}".format(randint3)
                    })
                self.success(result)
                return True
    