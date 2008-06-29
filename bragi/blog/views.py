#!/usr/bin/env python
#coding=utf-8

# Create your views here.
from django.shortcuts import render_to_response

import business

def BlogIndex(request, pageNo = 1):
    articles = business.GetArticles(int(pageNo))
    pagerLinks = business.GetPager(int(pageNo))
    username = request.COOKIES.get('user', '')
    if not pagerLinks:
        return render_to_response('blog/404.html')
    return render_to_response('blog/default.html', locals())

