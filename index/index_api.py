#!/usr/bin/env python
# encoding: utf-8

"""
@author: yigal
@file: index_api.py
@time: 2018/5/7 13:50
"""
import datetime


def date_time():
    now_time = datetime.datetime.now()
    old_time = now_time - datetime.timedelta(days=1)
    start_time = datetime.datetime.strptime(old_time.strftime('%Y-%m-%d'), '%Y-%m-%d')
    stop_time = datetime.datetime.strptime(now_time.strftime('%Y-%m-%d'), '%Y-%m-%d')

    return start_time, stop_time


def format_time():
    now_time = datetime.datetime.now()
    old_time = now_time - datetime.timedelta(days=1)
    start_time = datetime.datetime.strptime(old_time.strftime('%Y-%m-%d'), '%Y-%m-%d')
    stop_time = datetime.datetime.strptime(now_time.strftime('%Y-%m-%d'), '%Y-%m-%d')

    return start_time, stop_time
