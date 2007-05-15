#!/usr/bin/env python
#coding=utf-8

from BeautifulSoup import BeautifulSoup
import re
import urllib2

# -------
url = 'http://blog.sina.com.cn/u/49032c390100083x'
headers = { 'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
req = urllib2.Request(url, headers = headers)
page = urllib2.urlopen(req)

# -------
soup = BeautifulSoup(page)

#print soup.prettify()
#print soup('a')
imgList = []
for link in soup('a'):
    a = [tag.name for tag in link.findAll()]
    if u'img' in a:
        imgs = link('img')
        for img in imgs:
#            print img['src']
            imgList.append(img['src'])

print imgList


