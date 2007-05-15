#!/usr/bin/env python
#coding=utf-8
import sys
import pycurl

class Test:
    def __init__(self):
        self.contents = ''

    def body_callback(self, buf):
        self.contents = self.contents + buf
#        print >>sys.stderr, 'Testing', pycurl.version
        
t = Test()
c = pycurl.Curl()
c.setopt(c.URL, 'http://www.baidu.com/index.html')
c.setopt(c.WRITEFUNCTION, t.body_callback)
c.perform()
c.close()
print t.contents

