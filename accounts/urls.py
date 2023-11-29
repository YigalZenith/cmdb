#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:

import accounts.account


urlpatterns = patterns('',
    url(r'^login/$', "accounts.account.user_login"),
    url(r'^loginout/$', "accounts.account.logout_view"),
    url(r'menu/$', "accounts.account.menu_class"),
    url(r'^password/$', 'django.contrib.auth.views.password_change', {'template_name': 'accounts/user_editpassword.html', 'post_change_redirect': '/'}),
)


