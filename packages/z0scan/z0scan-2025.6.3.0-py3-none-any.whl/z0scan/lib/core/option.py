#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# w8ay 2019/6/29
# JiuZero 2025/5/15

import os
import threading
import time
from queue import Queue
import config
from colorama import init as cinit
from lib.core.common import random_UA, ltrim
from lib.core.data import path, KB, conf
from lib.core.log import dataToStdout, logger, colors
from lib.core.exection import PluginCheckError
from lib.core.loader import load_file_to_module
from lib.core.db import initdb
from lib.core.output import OutPut
from lib.core.settings import banner, DEFAULT_USER_AGENT
from lib.core.spiderset import SpiderSet
from thirdpart.console import getTerminalSize
from lib.patch.requests_patch import patch_all
from lib.patch.ipv6_patch import ipv6_patch


def setPaths(root):
    path.root = root
    path.certs = os.path.join(root, 'certs')
    path.scanners = os.path.join(root, 'scanners')
    path.data = os.path.join(root, "data")
    path.data_dict = os.path.join(root, "data", "dict")
    path.fingprints = os.path.join(root, "fingprints")
    path.output = os.path.join(root, "output")


def initKb():
    KB['continue'] = False  # 线程一直继续
    KB['registered'] = dict()  # 注册的漏洞插件列表
    KB['fingerprint'] = dict()  # 注册的指纹插件列表
    KB['task_queue'] = Queue()  # 初始化队列
    KB["spiderset"] = SpiderSet()  # 去重复爬虫
    KB['start_time'] = time.time()  # 开始时间
    KB["lock"] = threading.Lock()  # 线程锁
    KB["output"] = OutPut()
    KB["running_plugins"] = dict()
    KB['finished'] = 0  # 完成数量
    KB["result"] = 0  # 结果数量
    KB["running"] = 0  # 正在运行数量

    KB.limit = False
    KB.dicts = dict()
    KB.pause = False
    KB.esc_triggered = False

def initPlugins():
    # 加载检测插件
    for root, dirs, files in os.walk(path.scanners):
        files = filter(lambda x: not x.startswith("__") and x.endswith(".py"), files)
        for _ in files:
            q = os.path.splitext(_)[0]
            if conf.able and q not in conf.able and q != 'loader':
                continue
            if conf.disable and q in conf.disable:
                continue
            filename = os.path.join(root, _)
            mod = load_file_to_module(filename)
            try:
                mod = mod.Z0SCAN()
                mod.checkImplemennted()
                plugin = os.path.splitext(_)[0]
                plugin_type = os.path.split(root)[1]
                relative_path = ltrim(filename, path.root)
                if getattr(mod, 'type', None) is None:
                    setattr(mod, 'type', plugin_type)
                if getattr(mod, 'path', None) is None:
                    setattr(mod, 'path', relative_path)
                KB["registered"][plugin] = mod
            except PluginCheckError as e:
                logger.error('Not "{}" attribute in the plugin: {}'.format(e, filename))
            except AttributeError as e:
                logger.error('Filename: {} not class "{}", Reason: {}'.format(filename, 'Z0SCAN', e))
                raise
    logger.info('Load scanner plugins: {}{}{}'.format(colors.y, len(KB["registered"])-1, colors.e))

    # 加载指纹识别插件
    num = 0
    for root, dirs, files in os.walk(path.fingprints):
        files = filter(lambda x: not x.startswith("__") and x.endswith(".py"), files)
        for _ in files:
            filename = os.path.join(root, _)
            if not os.path.exists(filename):
                continue
            name = os.path.split(os.path.dirname(filename))[-1]
            mod = load_file_to_module(filename)
            if not getattr(mod, 'fingerprint'):
                logger.error("filename: {} load faild,not function 'fingerprint'".format(filename))
                continue
            if name not in KB["fingerprint"]:
                KB["fingerprint"][name] = []
            KB["fingerprint"][name].append(mod)
            num += 1
    logger.info('Load fingerprint plugins: {}{}{}'.format(colors.y, num, colors.e))
    
    # 加载模糊字典并储存为列表
    num = 0
    for root, dirs, files in os.walk(path.data_dict):
        files = list(filter(lambda x: x.endswith('.txt'), files))
        for _ in files:
            name = os.path.splitext(_)[0]
            file = os.path.join(path.data_dict, _)
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = [line.strip() for line in f.readlines() if line.strip()]
                    # TODO: replace
                    KB.dicts[name] = content
                    num += 1
            except Exception as e:
                logger.warning(f'Error loading dict {file}: {str(e)}')
    logger.info('Load fuzz dicts: {}{}{}'.format(colors.y, num, colors.e))


def _merge_options(cmdline):
    # 命令行配置 将覆盖 config配置
    if hasattr(cmdline, "items"):
        cmdline_items = cmdline.items()
    else:
        cmdline_items = cmdline.__dict__.items()
    for key, value in vars(config).items():
        conf[key.lower()] = value
        continue
    for key, value in cmdline_items:
        conf[key] = value
        continue


def _set_conf():
    # show version
    if conf.version:
        exit()

    # server_addr
    if isinstance(conf["server_addr"], str):
        if ":" in conf["server_addr"]:
            splits = conf["server_addr"].split(":", 2)
            conf["server_addr"] = tuple([splits[0], int(splits[1])])
        else:
            conf["server_addr"] = tuple([conf["server_addr"], conf.default_proxy_port])

    # threads
    conf["threads"] = int(conf["threads"])

    # proxy
    if isinstance(conf["proxy"], str) and "@" in conf["proxy"]:
        conf["proxy_config_bool"] = True
        method, ip = conf["proxy"].split("@")
        conf["proxy"] = {
            method.lower(): ip
        }

    # user-agent
    if conf.random_agent:
        conf.agent = random_UA()
    else:
        conf.agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101'


def _init_stdout():
    # 指定扫描等级
    logger.info("Level of contracting: [#{}{}{}]".format(colors.y, conf.level, colors.e))
    # 不扫描网址
    if len(conf["excludes"]):
        logger.info("No scanning: {}".format(repr(conf["excludes"])))
    # 指定扫描插件
    if conf.disable:
        logger.info("Not use plugins: {}".format(repr(conf.disable)))
    if conf.able:
        logger.info("Use plugins: {}".format(repr(conf.able)))
    if conf.ignore_waf:
        logger.warning('Ignore the presence of Waf.')
    if conf.html:
        logger.info("Html will be saved in '{}'".format(KB.output.get_html_filename()))
    logger.info("Result will be saved in '{}'".format(KB.output.get_filename()))

def env_check():
    # Check if running in Termux environment
    try:
        if 'com.termux' in os.environ.get('PREFIX', ""):
            KB.env = "termux"
            logger.warning("Keyboard listening will not work in Termux")
    except Exception as e:
        pass

def init(root, cmdline):
    cinit(autoreset=True)
    setPaths(root)
    dataToStdout(banner)
    _merge_options(cmdline)
    _set_conf()
    initKb()
    # env_check()
    initPlugins()
    initdb(root)
    _init_stdout()
    patch_all()
    ipv6_patch()