#!/usr/bin/env python
#coding=utf-8

from django.http import HttpResponseRedirect

def Index(request):
    return HttpResponseRedirect('blog')
    