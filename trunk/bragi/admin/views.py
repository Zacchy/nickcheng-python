#!/usr/bin/env python
#coding=utf-8

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect

def AdminIndex(request):
    response = render_to_response('admin/default.html')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if username == 'nickcheng' and password == '123456789':
            response = HttpResponseRedirect('../blog/')
            response.set_cookie('user', username)
            #request.session['user'] = username
        else:
            response = render_to_response('admin/default.html', {'loggedin': 1})
    return response

def Logout(request):
    response = HttpResponseRedirect('/blog/')
    response.delete_cookie('user')
    return response