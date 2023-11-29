#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib import admin
from models import *

class ServerAdmin(admin.ModelAdmin):
    list_display = ('hostname', 'eth1','create_time')
    search_fields = ('hostname','eth1')
    list_filter = ('create_time',)
    date_hierarchy = 'create_time'
    #ordering = ('-create_time',)
    #fields = ('hostname','eth1')
    filter_horizontal = ('service',)
    #raw_id_fields = ('service',)


class HostRecordAdmin(admin.ModelAdmin):
    list_display = ('host', 'user', 'time', 'content', 'comment')
    search_fields = ('host',)
    list_filter = ('time',)
    date_hierarchy = 'time'
    ordering = ('-time',)
# for cls in [IDC,ShoppingList,Project,Server]:
#     admin.site.register(cls)

class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('model', 'sn', 'buy_date')
    search_fields = ('sn',)
    list_filter = ('buy_date',)
    date_hierarchy = 'buy_date'
    ordering = ('-buy_date',)

admin.site.register(IDC)
admin.site.register(ShoppingList,ShoppingListAdmin)
admin.site.register(Project)
admin.site.register(Server,ServerAdmin)
admin.site.register(HostRecord,HostRecordAdmin)