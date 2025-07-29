#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# JiuZero 2025/5/22

import re
import copy, random, string
from urllib.parse import quote
from api import generateResponse, VulType, PLACE, Type, PluginBase, conf

class Z0SCAN(PluginBase):
    name = "crlf"
    desc = 'CRLF Injection'
    version = "2025.5.22"
    risk = 2

    def _check_response(self, resp, test_header):
        if test_header['header_name'] in resp.headers:
            return True, "headers"
        body_pattern = re.compile(
            rf"{test_header['header_name']}\s*:\s*{test_header['header_value']}", 
            re.I | re.M
        )
        if body_pattern.search(resp.text):
            return True, "body"
        
        return False, None

    def audit(self):
        if conf.level == 0 or not 2 in conf.risk or self.fingerprints.waf:
            return
        _payloads = [
            # 基础换行组合
            "\r\n",
            "\r\n\t",
        ]
        if conf.level == 3:
            _payloads += [
                "\r\t",
                "\n",
                "\r",
                "嘊嘍",    # Twitter风格
                "čĊ",      # Node.js风格
                "%0d%0a",  # URL编码
            ]
        rand_str = ''.join(random.choices(string.hexdigits, k=8)).lower()
        test_header = {
            'header_name': f"X-Z0SCAN-{rand_str}",
            'header_value': f"{rand_str}"
        }
        for _payload in _payloads:
            _payload = f"{_payload}{test_header['header_name']}: {test_header['header_value']}"
            iterdatas = self.generateItemdatas()
            for _ in iterdatas:
                k, v, position = _
                if position in [PLACE.JSON_DATA, PLACE.XML_DATA, PLACE.MULTIPART_DATA, PLACE.ARRAY_LIKE_DATA, PLACE.SOAP_DATA]:
                    continue
                payload = self.insertPayload({
                    "key": k,
                    "position": position,
                    "payload": _payload,
                })
                r = self.req(position, payload)
                if not r:
                    continue
                is_vuln, location = self._check_response(r, test_header)
                if not is_vuln:
                    continue
                
                result = self.generate_result()
                result.main({
                    "type": Type.REQUEST,
                    "url": self.requests.url,
                    "vultype": VulType.CRLF,
                    "show": {
                        "Payload": payload
                    }
                })
                result.step("Request1", {
                    "request": r.reqinfo,
                    "response": generateResponse(r),
                    "desc": f"Find {test_header['header_name']} in {location}"
                })
                self.success(result)
                return