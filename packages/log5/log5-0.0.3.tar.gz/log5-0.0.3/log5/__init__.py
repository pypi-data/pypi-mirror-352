#!/usr/bin/env python
# -*- coding: utf-8 -*-
#===============================================================================
#
# Copyright (c) 2017 <> All Rights Reserved
#
#
# File: /Users/hain/chat-log-burnish/purelog/common/log.py
# Author: Hai Liang Wang
# Date: 2017-10-25:16:58:57
#
#===============================================================================

"""
   
"""
from __future__ import print_function
from __future__ import division

__copyright__ = "Copyright (c) 2017 . All Rights Reserved"
__author__    = "Hai Liang Wang"
__date__      = "2017-10-25:16:58:57"


import os
import sys
import logging
import json
import env3

curdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(curdir)

if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding("utf-8")
    # raise "Must be using Python 3"

ENV = env3.read_env()

'''
日志输出
'''
OUTPUT_STDOUT = 1
OUTPUT_FILE = 2
OUTPUT_BOTH = 3

'''
日志级别
'''
CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0

'''
日志格式
'''
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_file = os.path.join(os.getcwd(), 'default.log')

LOG_LEVEL= "INFO" if not "LOG_LEVEL" in ENV else ENV["LOG_LEVEL"]
LOG_FILE= log_file if not "LOG_FILE" in ENV else ENV["LOG_FILE"]
print("[log5] logger settings LOG_FILE %s, LOG_LEVEL %s >> usage checkout https://github.com/hailiang-wang/python-log5" % (LOG_FILE, LOG_LEVEL))

# log would print twice with logging.basicConfig
# logging.basicConfig(level=LOG_LEVEL)

'''
Handlers
'''
fh = logging.FileHandler(log_file)
fh.setFormatter(formatter)
fh.setLevel(LOG_LEVEL)
ch = logging.StreamHandler()
ch.setFormatter(formatter)
ch.setLevel(LOG_LEVEL)

def set_log_level(level = "DEBUG"):
    fh.setLevel(level)
    ch.setLevel(level)

def get_logger(logger_name, output_mode = OUTPUT_STDOUT):
    logger = logging.getLogger(logger_name)

    if output_mode == OUTPUT_STDOUT:
        logger.addHandler(ch)

    if output_mode == OUTPUT_FILE:
        logger.addHandler(fh)

    if output_mode == OUTPUT_BOTH:
        logger.addHandler(fh)
        logger.addHandler(ch)

    logger.setLevel(DEBUG)

    return logger


def pretty(j, indent=4, sort_keys=True):
    """
    get dict object/json as pretty string
    :param j:
    :return:
    """
    return json.dumps(j, indent=indent, sort_keys=sort_keys, ensure_ascii=False, default=str)


def LN(x):
    """
    log name 获得模块名字，输出日志短名称
    LN(__name__)
    """
    return x.split(".")[-1]

if __name__ == "__main__":
    logger = get_logger(LN(__name__), output_mode=OUTPUT_BOTH)
    logger.debug('bar')
    logger.info('foo')