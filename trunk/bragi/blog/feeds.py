#!/usr/bin/env python
#coding=utf-8

from django.http import HttpResponse
#from django.template.loader import get_template
#from django.template import Context

import business
import g

def BlogIndex(request):
    articles = business.GetArticles(1, g.Get().INDEXPAGE_ARTICLECOUNT_RSS)
    rss = business.Articles2RSS(articles)
#    t = get_template('feeds/default.xml')
#    html = t.render(Context({'rss': rss}))
    return HttpResponse(rss.writeString('utf8'), mimetype='text/xml')
        
        