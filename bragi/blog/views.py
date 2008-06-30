#!/usr/bin/env python
#coding=utf-8

# Create your views here.
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect

import business

def BlogIndex(request, pageNo = 1):
    articles = business.GetArticles(int(pageNo))
    pagerLinks = business.GetPager(int(pageNo))
    username = request.COOKIES.get('user', '')
    if not pagerLinks:
        return render_to_response('blog/404.html')
    return render_to_response('blog/default.html', locals())

# Admin 
def AdminIndex(request):
    response = render_to_response('blog/admin/default.html')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if username == 'nickcheng' and password == '123456789':
            response = HttpResponseRedirect('/blog/admin/write/')
            response.set_cookie('user', username)
            #request.session['user'] = username
        else:
            response = render_to_response('blog/admin/default.html', {'loggedin': 1})
    return response

def Logout(request):
    response = HttpResponseRedirect('/blog/')
    response.delete_cookie('user')
    return response

def Write(request):
    username = request.COOKIES.get('user', '')
    if not username:
        response = HttpResponseRedirect('/blog/admin/login/')
    else:
        inputError = False
        if request.method == 'POST':
            title = request.POST['title']
            slug = request.POST['slug']
            content = request.POST['content']
            if not title or not slug or not content:
                inputError = True
            else:
                business.save_article(title, slug, content)
        response = render_to_response('blog/admin/write.html', locals())
    return response
