#!/usr/bin/env python
#coding=utf-8

# Create your views here.
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect

import business

def BlogIndex(request, pageNo = 1):
    headerInfo = business.GetHeaderInfo()
    articles = business.GetArticles(int(pageNo))
    pagerLinks = business.GetPager(int(pageNo))
    username = request.COOKIES.get('user', '')
    if not pagerLinks:
        return render_to_response('blog/404.html')
    return render_to_response('blog/default.html', locals())

def SingleArticle(request, year, month, day, slug):
    headerInfo = business.GetHeaderInfo()
    article = business.GetArticle(year, month, day, slug)
    comments = business.GetComments(article.ID)
    username = request.COOKIES.get('user', '')
    return render_to_response('blog/singlearticle.html', locals())

# Admin 
def AdminIndex(request):
    headerInfo = business.GetHeaderInfo()
    response = render_to_response('blog/admin/default.html', locals())
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if username == 'nickcheng' and password == '123456789':
            response = HttpResponseRedirect(headerInfo['homeURL'] + 'admin/write/')
            response.set_cookie('user', username)
            #request.session['user'] = username
        else:
            response = render_to_response('blog/admin/default.html', {'loggedin': 1})
    return response

def Logout(request):
    headerInfo = business.GetHeaderInfo()
    response = HttpResponseRedirect(headerInfo['homeURL'])
    response.delete_cookie('user')
    return response

def Write(request):
    headerInfo = business.GetHeaderInfo()
    username = request.COOKIES.get('user', '')
    if not username:
        response = HttpResponseRedirect(headerInfo['homeURL'] + 'admin/login/')
    else:
        inputError = False
        response = render_to_response('blog/admin/write.html', locals())
        if request.method == 'POST':
            title = request.POST['title']
            slug = request.POST['slug']
            content = request.POST['content']
            if not title or not slug or not content:
                inputError = True
            else:
                business.save_article(title, slug, content)
                response = HttpResponseRedirect(headerInfo['homeURL'])
    return response
