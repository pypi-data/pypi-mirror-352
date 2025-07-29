#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# w8ay 2019/7/4
# JiuZero 2025/5/7

from urllib.parse import urlparse
from copy import deepcopy
import requests, re
from lib.controller.controller import task_push
from lib.core.common import isListLike, get_parent_paths
from lib.core.data import conf, KB
from lib.core.log import logger, colors
from lib.core.wafDetector import detector
from lib.core.enums import HTTPMETHOD
from lib.core.plugins import PluginBase
from lib.parse.parse_request import FakeReq
from lib.parse.parse_response import FakeResp
from lib.core.db import selectdb, insertdb
from lib.core.settings import notAcceptedExt


class Z0SCAN(PluginBase):
    name = 'loader'
    desc = 'plugin loader'

    def audit(self):
        if KB.pause:
            return
        headers = deepcopy(self.requests.headers)
        url = deepcopy(self.requests.url)

        # 跳过一些扫描
        if self.requests.suffix in notAcceptedExt:
            return
        for rule in conf.excludes:
            if rule in self.requests.netloc:
                logger.info("Skip Domain: {}".format(url))
                return
            
        # 跳过前台的同一功能页（通常为文章页）
        itemdates = self.generateItemdatas()
        params = ""
        _url = re.sub(r'([/_?&=-])(\d+)', "0", url).split('?')[0]
        _params = {}
        if not len(itemdates) > 6:
            for _ in itemdates:
                k, v, position = _
                if str(v).isdigit():
                    v = "0"
                _params[k] = v
            params = str(sorted(_params.items())).replace('\'', '"')
            history = selectdb("CACHE", "HOSTNAME", where="URL='{}' AND PARAMS='{}'".format(_url, params))
            if history and conf.skip_similar_url:
                logger.info("Skip URL: {}".format(url))
                return

        logger.debug(itemdates, origin='iterdatas', level=1)
        
        # Waf检测
        if not conf.ignore_waf:
            while KB.limit:
                pass
            detector(self)
            KB.limit = False

        if params:
            cv = {
                'HOSTNAME': self.requests.hostname,
                'URL': _url,
                'PARAMS': params,
            }
        else:
            cv = {
                'HOSTNAME': self.requests.hostname,
                'URL': _url,
                'PARAMS': '',
            }
        insertdb("CACHE", cv)
        
        lower_headers = {k.lower(): v for k, v in self.response.headers.items()}
        for name, values in KB["fingerprint"].items():
            for mod in values:
                m, version = mod.fingerprint(self.requests.suffix.lower(), lower_headers, self.response.text)
                if isinstance(m, str):
                    if name == "os" and m not in self.fingerprints.os:
                        self.fingerprints.os[m] = version
                    elif name == "webserver" and m not in self.fingerprints.webserver:
                        self.fingerprints.webserver[m] = version
                    elif name == "programing" and m not in self.fingerprints.programing:
                        self.fingerprints.programing[m] = version
        
        # PerFile
        if KB["spiderset"].add(url, 'PerFile'):
            task_push('PerFile', self.requests, self.response)

        # PerServer
        domain = "{}://{}".format(self.requests.scheme, self.requests.netloc)
        if KB["spiderset"].add(domain, 'PerServer'):
            req = requests.get(domain, headers=headers, allow_redirects=False)
            fake_req = FakeReq(domain, headers, HTTPMETHOD.GET, "")
            fake_resp = FakeResp(req.status_code, req.content, req.headers)
            task_push('PerServer', fake_req, fake_resp)

        # PerFolder
        urls = set(get_parent_paths(url))
        for parent_url in urls:
            if not KB["spiderset"].add(parent_url, 'get_link_directory'):
                continue
            req = requests.get(parent_url, headers=headers, allow_redirects=False)
            if KB["spiderset"].add(req.url, 'PerFolder'):
                fake_req = FakeReq(req.url, headers, HTTPMETHOD.GET, "")
                fake_resp = FakeResp(req.status_code, req.content, req.headers)
                task_push('PerFolder', fake_req, fake_resp)
