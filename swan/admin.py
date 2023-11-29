#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib import admin
from models import *


class OnlineLogAdmin(admin.ModelAdmin):
    list_display = ('username', 'optime', 'action', 'command', 'tag', 'hname', 'result')
    search_fields = ('tag',)
    list_filter = ('optime',)
    date_hierarchy = 'optime'
    ordering = ('-optime',)


class OnlineRecordLogAdmin(admin.ModelAdmin):
    list_display = ('username', 'optime', 'action', 'URL', 'MD5')
    search_fields = ('MD5',)
    list_filter = ('optime',)
    date_hierarchy = 'optime'
    ordering = ('-optime',)


admin.site.register(OnlineLog, OnlineLogAdmin)
admin.site.register(OnlineRecordLog, OnlineRecordLogAdmin)
