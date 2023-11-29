# !/usr/bin/env python
#-*- coding: utf-8 -*-
import datetime
from django import template

register = template.Library()

def current_time(format_string):
    return datetime.datetime.now().strftime(format_string)

register.simple_tag(current_time)

def editor(context):
    return {}
register.inclusion_tag('saltstack/editor.html', takes_context=True)(editor)
