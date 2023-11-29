#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()
urlpatterns = patterns('',
                       url(r'^$', 'index.views.index'),
                       url(r'^ztree_host_detail/$', 'index.views.ztree_host_detail'),
                       url(r'accounts/', include("accounts.urls")),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'assets/', include("assets.urls")),
                       url(r'swan/', include("swan.urls")),
                       url(r'docs/', 'index.views.docs'),
                       url(r'test/', 'mysite.views.test'),
                       (r'^/admin/jsi18n/', 'django.views.i18n.javascript_catalog'),
                       )
