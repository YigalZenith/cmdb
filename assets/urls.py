#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from assets import views
urlpatterns = patterns('',
                       # 机房操作
                       url(r'^idc_add/$', "assets.views.idc_add"),
                       url(r'^idc_list/$', "assets.views.idc_list"),
                       url(r'^idc_edit/$', "assets.views.idc_edit"),
                       url(r'^idc_del/$', "assets.views.idc_del"),
                       
                       # 采购操作
                       url(r'^shopping_list/$', "assets.views.shopping_list"),
                       url(r'^shopping_info_ajax/$', "assets.views.shopping_info_ajax"),
                       url(r'^shopping_add/$', "assets.views.shopping_add"),
                       url(r'^shopping_edit/$', "assets.views.shopping_edit"),
                       url(r'^shopping_del/$', "assets.views.shopping_del"),

                       # 主机管理
                       url(r'^host_list/$', "assets.views.host_list"),
                       url(r'^change_info_ajax/$', "assets.views.host_search"),
                       url(r'^host_search/$', "assets.views.host_search"),
                       url(r'^host_detail/$', "assets.views.host_detail", name="host_detail"),
                       url(r'^host_add/$', "assets.views.host_add"),
                       url(r'^host_del/$', "assets.views.host_del", name='host_del'),
                       url(r'^host_edit/$', "assets.views.host_edit", name="host_edit"),
                       url(r'^host_add_batch/$', "assets.views.host_add_batch"),
                       url(r'^host_del_batch/$', "assets.views.host_del_batch"),
                       url(r'^host_edit_batch/$', "assets.views.host_edit_batch"),                    
                       )
