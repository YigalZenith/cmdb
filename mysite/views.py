#!/usr/bin/env python
# -*- coding: utf-8 -*-


from django.http import HttpResponse


def test(request):
    print request.GET['a']
    username2 = request.GET.get('username', '')
    password = request.GET.get('password', '')
    return HttpResponse(username+":"+password)
