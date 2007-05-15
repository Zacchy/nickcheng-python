#!/usr/bin/env python
#coding = gbk

import os
import urllib
import urllib2
import re
import socket

def getImageURL(url):
    domainName = os.path.split(url)[0]
    
    socket.setdefaulttimeout(60.0)
    s = urllib.urlopen(url)
    str = s.read()
    
    result = re.search("<img[^>]+?id=\"thepic\"[^>]+src=\"([^\"]+)\".*>", str, re.I)
    fileName = result.group(1)
    if fileName.find('http') >= 0:
        return fileName
    else:
        return (domainName + "/" + fileName)
    
def getImageURL2(url):
    domainName = os.path.split(url)[0]
    
    socket.setdefaulttimeout(60.0)
    
    proxy_support = urllib2.ProxyHandler({"http":"http://143.248.139.169:3124"})
    opener = urllib2.build_opener(proxy_support)
    urllib2.install_opener(opener)
    
    s = urllib2.urlopen(url)
    str = s.read()

    result = re.search("<img[^>]+?id=\"thepic\"[^>]+src=\"([^\"]+)\".*>", str, re.I)
    fileName = result.group(1)
    if fileName.find('http') >= 0:
        return fileName
    else:
        return (domainName + "/" + fileName)
    
if __name__ == '__main__':
    print "input:",
    u = raw_input()
    print getImageURL2(u)
    