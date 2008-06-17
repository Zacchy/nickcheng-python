#!/usr/bin/env python
#coding=utf-8

# Create your views here.
from django.shortcuts import render_to_response
import datetime

import business

def BlogIndex(request):
    articles = business.getArticles(1)
    return render_to_response('blog/default.html', locals())

def test(request):
    names = dbaccess.test()
    return render_to_response('blog/default.html', locals())