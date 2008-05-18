#!/usr/bin/env python
#coding=utf-8

import pycurl

class Page:
    '''
    页面类
    用于抓取页面源代码
    
    依赖: pycurl
    
    属性:
        . Content: 页面的源代码
    
    方法:
    
    例子:
        1. 普通使用
            p = Page('http://www.datasheetcatalog.com/function/index.html')
            print p.Content
        2. 使用代理
            p = Page('http://www.datasheetcatalog.com/function/index.html', 'http://201.216.247.77:8080')
            print p.Content
        
    '''
    def __init__(self, url, proxy = ''):
        self.Content = ''
        self.Url = url
        self.Proxy = proxy
        
        if self._isFile():
            self._getFileContent()
        else:
            self.Refresh2()
    
    def Refresh2(self):
        '''
        '''
        import sys, urllib
        wp = urllib.urlopen(self.Url)
        self.Content = wp.read()
        wp.close()
    
    def Refresh(self):
        '''
        '''
        c = pycurl.Curl()
        c.setopt(c.URL, self.Url)
        if self.Proxy != '': # 如果有代理服务器, 则使用代理服务器
            c.setopt(pycurl.PROXY, self.Proxy)
        c.setopt(c.WRITEFUNCTION, self._refresh_callback)
        c.perform()
        c.close()
    
    def _refresh_callback(self, buf):
        self.Content += buf
        
    def _isFile(self):
        u = self.Url
        if u.lower()[:4]=='http':
            return False
        else:
            return True

    def _getFileContent(self):
        f = file(self.Url, 'r')
        self.Content = f.read()

if __name__ == '__main__':
    p = Page('http://www.datasheetcatalog.com/function/index.html', 'http://218.185.66.30:80')
    # http://201.216.247.77:8080
    # http://212.149.169.175:8080
    # http://202.70.36.74:8080
    print p.Content