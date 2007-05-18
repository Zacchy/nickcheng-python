#!/usr/bin/env python
#coding=utf-8

# PictureDownloader

from BeautifulSoup import BeautifulSoup
import re
import urllib2

import nUtils

class URL2IMGList:
    '''
    . 单页面URL    . 页面代码
        . 提取页面代码的时候要去掉Refer头    . 提取所需列表        V IMG标签的SRC值        V 包含有IMG标签的A标签的HREF值        V 相对路径要补全    '''
    def __init__(self, url):
        '''
        构造方法, 模拟IE 5.5的UA
        '''
        self.url = url
        self.urlPrefix = nUtils._getURLPrefix(url)
        self.headers = { 'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
        
    def _getIMG(self, soup, all = False):
        '''
        获取所有IMG标签的SRC值
        Get list of SRCs of "IMG" tag
        <img src="xxx" />
        
        . all: 是否获取只有相对路径的图片。一般只有相对路径的图片都不是重要图片
            . True: 获取所有图片，包括相对路径的图片
            . False: 只获取有绝对路径的图片
        '''
        imgList = []
        for img in soup('img'):
            src = img['src']
            if not src.startswith('http'):
                if all:
                    src = self.urlPrefix + '/' + src
                else:
                    continue
            if src not in imgList:
                imgList.append(src)
        
        return imgList

    def _getAIMG(self, soup):
        '''
        获取所有内含有IMG标签的A标签的HREF值
        Get list of HREFs of "A" tag who has a child named "IMG"
        <a href="xxx"><img src="" /></a>
        '''
        imgList = []        for link in soup('a'):            print link            a = [tag.name for tag in link.findAll()]            if u'img' in a:                if dict(link.attrs).has_key('href'):
                    imgList.append(link['href'])
                
        return imgList
                    
    def _getSoup(self):
        ''''''
        req = urllib2.Request(self.url, headers = self.headers)        page = urllib2.urlopen(req)        soup = BeautifulSoup(page)
        return soup
        
                    
    def GetIMG(self, all = False):
        '''
        获取所有IMG标签的SRC值
            . all: 是否获取只有相对路径的图片。一般只有相对路径的图片都不是重要图片
                . True: 获取所有图片，包括相对路径的图片
                . False: 只获取有绝对路径的图片
        '''
        soup = self._getSoup()
        result = self._getIMG(soup, all)
        
        return result
    
    def GetAIMG(self):
        '''
        获取所有内含有IMG标签的A标签的HREF值
        '''
        soup = self._getSoup()
        result = self._getAIMG(soup)
        return result
def testGetIMG():    ''''''    url = 'http://www.kawaiination.com/community/showthread.php?t=7173'    geter = URL2IMGList(url)    result = geter.GetIMG(True)    for link in result:        print link
def testGetAIMG():
    ''''''
    url = 'http://www.kawaiination.com/community/showthread.php?t=7173'
    geter = URL2IMGList(url)
    result = geter.GetAIMG()
    for link in result:
        print link
    
if __name__ == '__main__':
#    main()
#    testGetIMG()
    testGetAIMG()
    
def main():
    ''''''
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

