#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# JiuZero 2025/3/18

import re
import random
import string
from api import generateResponse, VulType, PLACE, Type, PluginBase, KB, conf, logger
from concurrent.futures import ThreadPoolExecutor, as_completed

class Z0SCAN(PluginBase):
    name = "xpathi-error"
    desc = 'XPath Injection'
    version = "2025.3.18"
    risk = 2

    def condition(self):
        if conf.level == 0 or not 2 in conf.risk:
            return False
        if not self.fingerprints.waf:
            return True
        return False

    def _detect_errors(self, response_text):
        error_patterns = {
            'exact': [
                'MS.Internal.Xml.',
                'org.apache.xpath.XPath',
                'Expression must evaluate to a node-set',
                'System.Xml.XPath.XPathException'
            ],
            'regex': [
                r"XPathException: .*?'(?P<detail>.+?)'",
                r"Line \d+: Invalid expression",
                r"at (org\.apache\.xpath|javax\.xml\.xpath)",
                r"Error code: 0x[0-9a-fA-F]+ \(XPath\)"
            ]
        }
        if not response_text:
            return False, None
        # 精确匹配
        for pattern in error_patterns['exact']:
            if pattern in response_text:
                return True, f"Exact Match {pattern}"
        # 正则匹配
        for regex in error_patterns['regex']:
            match = re.search(regex, response_text, re.I)
            if match:
                detail = match.groupdict().get('detail', match.group(0))
                return True, f"Regex Match {detail}"
        return False, None

    def audit(self):
        if not self.condition():
            return
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
        rand_num = random.randint(1000, 9999)
        _payloads = [
            # 基础闭合测试
            "\"')", "<!--",
            # 特殊字符组合
            "]]>", "*/*", "]["
        ]
        if conf.level >= 2:
            _payloads += [
                # 错误诱导
                f"convert({rand_num}, 'invalid_type')",
            ]
        if conf.level == 3:
            _payloads += [
                # 表达式测试
                f"][{rand_num}]", 
                f" or {rand_num}={rand_num}",
                f"|//*[contains(.,{rand_num})]", 
                # 函数测试
                f"count(//*[position()={rand_num}])",
            ]
        for _payload in _payloads:
            payload = self.insertPayload({
                "key": k, 
                "value": v, 
                "position": position, 
                "payload": _payload
                })
            r = self.req(position, payload)
            if not r or r.status_code >= 500:
                continue
            is_vuln, error_info = self._detect_errors(r.text)
            if not is_vuln:
                continue
            result = self.generate_result()
            result.main({
                "type": Type.REQUEST, 
                "url": self.requests.url, 
                "vultype": VulType.OTHER, 
                "show": {
                    "Position": f"{position} > {k}",
                    "Payload": payload
                    }
                })
            result.step("Request1", {
                "request": r.reqinfo, 
                "response": generateResponse(r), 
                "desc": f"{error_info}"
                })
            self.success(result)
            return