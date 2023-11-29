#!/usr/bin/env python
# encoding: utf-8

"""
@author: yigal
@file: swan_api.py
@time: 2018/4/27 13:31
"""

from swan.models import OnlineLog, OnlineRecordLog


def add_onlinerecordlog(username, action, url, md5):
    obj = OnlineRecordLog(username=username, action=action, URL=url, MD5=md5)
    obj.save()


def add_onlinelog(username, action, command, tag, pname, hid, hname, result):
    obj = OnlineLog(username=username, action=action, command=command, tag=tag, pname=pname, hid=hid, hname=hname, result=result)
    obj.save()
