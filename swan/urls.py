#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns,url

urlpatterns = patterns('',                       
                       # 项目管理
                       url(r'^project_list/$', "swan.views.project_list", name="project_list"),
                       url(r'^project_add/$', "swan.views.project_add"),
                       url(r'^project_del/$', "swan.views.project_del"),
                       url(r'^project_edit/$', "swan.views.project_edit"),

                       # 联合online_record表，返回war包上线历史记录
                       url(r'^project_history/$', "swan.views.project_history"),
                       # 筛选只需要查询的项目
                       url(r'^project_history_filter/$', "swan.views.project_history_filter"),
                       # war包上线历史中，添加按钮打开iframe窗口时调用
                       url(r'^project_upload/$', "swan.views.project_upload"),
                       # 上传online_record表数据，记录上线人员。 定义puppet-master/salt-master的位置
                       url(r'^project_update/$', "swan.views.project_update"),
                       # 根据war包上线历史记录，打开iframe窗口并自动填充值
                       url(r'^project_rollback/$', "swan.views.project_rollback"),
                       # 删除online_record表数据
                       url(r'^project_remove/$', "swan.views.project_remove"),

                       # 定义了项目发布页面,联合查询项目表和服务器表
                       # 通过ajax调用url(r'^change_project_ajax/$', "assets.views.host_search"),筛选需要上线的项目
                       url(r'^project_deploy/$', "swan.views.project_deploy"),
                       url(r'^change_project_ajax/$', "assets.views.host_search"),
                       # 定义了上线的命令
                       url(r'^project_online/$', "swan.views.project_online"),
                       # url(r'^project_online_batch/$', "swan.views.project_online_batch"),
                       # 定义了记录日志文件的位置，并返回查看日志的html
                       # 通过ajax调用url(r'^project_log_handle/$', "swan.views.project_log_handle")，往查看日志的html中追加最新日志
                       url(r'^project_log/$', "swan.views.project_log"),
                       url(r'^project_log_handle/$', "swan.views.project_log_handle"),
                       # url(r'^get_log_endline/$', "swan.views.get_log_endline"),

                       # 项目发布页面的执行命令按钮，弹出iframe窗口
                       url(r'^execute_command/$', "swan.views.execute_command"),
                       # 执行命令弹出的iframe窗口的运行按钮点击时调用ajax时使用
                       url(r'^execute_command2/$', "swan.views.execute_command2"),

                       # 首页发布日志查询
                       url(r'onlinelog/(?P<pname>[a-z]+[0-9]*)/$', "swan.views.filter_online_log", name="filter_online_log"),

                       # salt推送功能
                       url(r'^push_zabbix/$', "swan.views.push_zabbix"),
                       url(r'^push_cmd/$', "swan.views.push_cmd"),
                       url(r'^push_module/$', "swan.views.push_module"),
                       )
