#!/usr/bin/env python
#coding=utf-8

def _getURLPrefix(url):
    ''''''
    import urllib2
    params = urllib2.urlparse.urlparse(url)
    
    if params[0] == '':
        return ''
    
    result = params[0] + '://' + params[1]
    
    li = params[2].rfind('/')
    if li > 0:
        result += params[2][:li]
        
    return result

