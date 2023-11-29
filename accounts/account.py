#!/usr/bin/python
# -*-coding:utf-8-*-

from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib import auth
from forms import LoginForm
import json


def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect(request.GET['next'])
            else:
                return render_to_response('accounts/login.html', RequestContext(request, {'form': form,'password_is_wrong':True}))
            
    return render_to_response('accounts/login.html', locals(), context_instance=RequestContext(request))


def logout_view(request):
    # auth.logout(request)
    request.session.flush()
    return HttpResponseRedirect("/")


def menu_class(request):
    user = request.user.username
    try:
        menu = auth.models.User.objects.get(username=user)
        if menu.menu_status:
            menu.menu_status = False
            menu.save()
        else:
            menu.menu_status = True
            menu.save()

        content = {"status": 200, "message": "update is ok"}
    except Exception,e:
        content = {"status": 403, "message": "what ary you doing"}
    return HttpResponse(json.dumps(content, ensure_ascii=False, indent=4, ))
