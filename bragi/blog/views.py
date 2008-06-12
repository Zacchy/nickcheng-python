# Create your views here.
from django.shortcuts import render_to_response
import datetime
import dbaccess

def BlogIndex(request):
    now = datetime.datetime.now()
    return render_to_response('blog/default.html', locals())

def test(request):
    names = dbaccess.test()
    return render_to_response('blog/default.html', locals())