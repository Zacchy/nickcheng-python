#!/usr/bin/env python
#coding=utf-8

import g

def IndexURL(pageNo):
    url = ['http://']
    url.append(g.Get().SITE_DOMAINPREFIX)
    url.append('/page/')
    url.append(str(pageNo))
    url.append('/')
    return ''.join(url)
