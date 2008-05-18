#!/usr/bin/env python
#coding=utf-8

# Something to get

from page import Page
from BeautifulSoup import BeautifulSoup
import re
import codecs
import os

LINE = 7
COLUMN = 10
GIRLURL = 'http://www.bobx.com/av-idol/%s/gallery-%s-%s-%s-%s.html'
PICPATTERN = 'http://www.bobx.com/av-idol/%s/%s-%s.jpg'

def main():
    ''''''
    mainURL = 'http://www.bobx.com/av-idol/'

    print 'Getting Girl Names......'
    girlList = GetGirlName(mainURL)
    print 'Got %d Girl.' % len(girlList)

    print 'Processing Every Girl......'
    for name in girlList:
        print '======='
        print 'Name: ' + name
        if not os.path.exists(name+'.txt'): # 如果文件已经存在则不覆盖
            ProcessGirl(name)

def GetGirlName(url):
    u = url
    c = Page(u).Content
    s = BeautifulSoup(c)

    t1 = s.findAll('div', {'class':'whitesmall'})
    nameList = []
    for d in t1:
        a = d('a')
        n = ''
        if len(a) == 2:
            n = a[1]['href'][:-1]
        else:
            n = a[0]['href'][:-1]
        if len(n) > 0:
            nameList.append(n)

    return nameList

def ProcessGirl(name):
    n = name
    girlPageURL = GIRLURL % (name, name, '%s', LINE, COLUMN)
    picURL = PICPATTERN % (name, name, '%s')
    pageSize = LINE * COLUMN
    links = []
    index = 0

    while True:
        u = girlPageURL % index
        print 'URL:' + u

        print 'Getting Pic from %d......' % index
        nos = GetPicNo(u)
        print 'Got %d Pic.' % len(nos)

        for no in nos:
            l = picURL % no.zfill(8)
            links.append(l)

        if len(nos) < pageSize:
            break
        index += pageSize

    print 'Saving to file......'
    SaveListToFile(name+'.txt', links)

def GetPicNo(url):
    u = url
    c = Page(u).Content
    s = BeautifulSoup(c)

    t1 = s.findAll('div', {'class':'redmini'})
    nl = []
    for t in t1:
        img = t.previousSibling()[0]
        alt = img['alt']
        n = alt[alt.rfind('-') + 2:]
        nl.append(n)

    return nl

def SaveListToFile(fileName, list):
    '''
    将列表保存为文件
    参数:
        filename: 要保存为的文件名
        list: 要保存的列表
    '''
    fn = FileNameFix(fileName)
    if os.path.exists(fn): # 如果文件已经存在则不覆盖
        return
    f = file(fn, 'w')
    for l in list:
        f.write(l.encode('utf-8'))
        f.write('\r\n')
    f.close()

def FileNameFix(name):
    n = name
    iv = '\/:,*?"\'<>|'
    for v in iv:
        n = n.replace(v, '')
    return n

if __name__ == '__main__':
    main()
