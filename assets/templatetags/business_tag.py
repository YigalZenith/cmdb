#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ast
import json

from django import template
from assets.models import Server, Project, ShoppingList

register = template.Library()

@register.filter(name='business_list')
def business_list(host):
    cmdb_data = Server.objects.get(pk=host)
    data = cmdb_data.service.all()

    business_all = []
    for i in data:
        business_all.append(i.service_name)

    return business_all

@register.filter(name='business_service')
def business_service(name):
    s = []
    bus_data = Project.objects.get(service_name=name)
    server_list = Server.objects.filter(business=bus_data).order_by("id")

    for i in server_list:
        t = i.service.all()
        for b in t:
            if b not in s:
                s.append(b)

    return s


@register.filter(name='group_str2')
def groups_str2(group_list):
    if len(group_list) < 3:
        return ' '.join([group.name for group in group_list])
    else:
        return '%s ...' % ' '.join([group.name for group in group_list[0:2]])


# @register.filter(name='str_to_list')
# def str_to_list(info):
#     return json.loads(info)

@register.filter(name='str_to_list')
def vms_liststr_to_list(info):
    info = ast.literal_eval(info.encode("utf-8"))
    return info


@register.filter(name='vms_list')
def vms_list(host):
    hostobjs = Server.objects.filter(vm=host)
    return hostobjs

@register.filter(name='ipaddr_list')
def ipaddr_list(shopping_obj):
    #ipaddr_obj = ShoppingList.objects.get(pk=shopping_obj)
    data = shopping_obj.ipaddr.all()

    ipaddr_all = []
    for i in data:
        ipaddr_all.append(i.eth1)

    ipaddr_all.sort(key=lambda s: map(int, s.split('.')))
    return ipaddr_all