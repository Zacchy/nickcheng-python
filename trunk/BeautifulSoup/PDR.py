#!/usr/bin/env python
#coding=utf-8

# PictureDownloader

from BeautifulSoup import BeautifulSoup
import re
import urllib2

class URL2IMGList:
    '''
    . 单页面URL    . 页面代码    . 提取所需列表        V IMG标签的SRC值        V 包含有IMG标签的A标签的HREF值        . 相对路径要补全    '''
    def __init__(self, url):
        '''
        构造方法, 模拟IE 5.5的UA
        '''
        self.url = url
        self.headers = { 'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
        
    def _getIMG(self, soup):
        '''
        获取所有IMG标签的SRC值
        Get list of SRCs of "IMG" tag
        <img src="xxx" />
        '''
        imgList = []
        for img in soup('img'):
            imgList.append(img['src'])
        
        return imgList

    def _getAIMG(self, soup):
        '''
        获取所有内含有IMG标签的A标签的HREF值
        Get list of HREFs of "A" tag who has a child named "IMG"
        <a href="xxx"><img src="" /></a>
        '''
        imgList = []        for link in soup('a'):            a = [tag.name for tag in link.findAll()]            if u'img' in a:                imgs = link('img')                for img in imgs:                    imgList.append(img['src'])
                    
    def _getSoup(self):
        ''''''
        req = urllib2.Request(self.url, headers = self.headers)        page = urllib2.urlopen(req)        soup = BeautifulSoup(page)
        return soup        
                    
    def GetIMG(self):
        '''
        获取所有IMG标签的SRC值
        '''
        soup = self._getSoup()
        result = self._getIMG(soup)
        
        return result
    
    def GetAIMG(self):
        '''
        获取所有内含有IMG标签的A标签的HREF值
        '''
        soup = self._getSoup()
        result = self._getAIMG(soup)
        return result
    
if __name__ == '__main__':
    # -------
    print "Let's begin!"
    downloadList = []
    url = 'http://www.kawaiination.com/community/showthread.php?t=7173'
    print 'URL: ' + url
    
    for i in range(1, 99):
        print 'Page %s is Processing...' % str(i)
        suburl = url + '&page=' + str(i)
        geter = URL2IMGList(suburl)
        result = geter.GetIMG()
        
        for link in result:
            if link.startswith('http') and link not in downloadList:
                downloadList.append(link)
            
    wfile = file('list.txt', 'w')
    wfile.write('\r\n'.join(downloadList))
    wfile.close()
    
    print result
#    headers = { 'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
#    req = urllib2.Request(url, headers = headers)
#    page = urllib2.urlopen(req)

    # -------
#    soup = BeautifulSoup(page)



