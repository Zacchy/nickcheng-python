#!/usr/bin/env python
#coding=utf-8

# Something to get

from page import Page
from BeautifulSoup import BeautifulSoup
import re
import codecs
import os

def main():
    ''''''
##    mainUrl = 'http://www.yeeyan.com/articles/view/freeyiyu/4356'
##    content = GetArticle(mainUrl)

##    classUrl = 'http://www.yeeyan.com/main/view/business?show=100&page=1'
##    links = GetClassLinks(classUrl)

    catLinks = GetClassUrl()
    for cat in catLinks:
        cl = cat.replace('index', 'view') + '?show=100&page=1'
        links = GetClassLinks(cl)
        for link in links:
            print 'Processing: ' + link
            title, content = GetArticle(link)
            if title == '':
                continue
            SaveFile(link, title, content)
    
def SaveFile(url, title, content):
    fn = title + '.txt'
    if os.path.exists(fn): # 如果文件已经存在则不覆盖
        return
    f = file(FileNameFix(fn), 'w')
    f.write(url.encode('utf-8'))
    f.write('\r\n')
    f.write(title.encode('utf-8'))
    f.write('\r\n')
    f.write(content.encode('utf-8'))
    f.close()

def FileNameFix(name):
    n = name
    iv = '\/:,*?"\'<>|'
    for v in iv:
        n = n.replace(v, '')
    return n

def GetClassUrl():
    ''''''
    mainUrl = 'http://www.yeeyan.com/main/index/all'
    pageContent = Page(mainUrl).Content
    soup = BeautifulSoup(pageContent)
    
    urlPrefix = 'http://www.yeeyan.com'
    catDivs = soup.findAll('div', {'class':'catDiv'})

    links = []
    for div in catDivs:
        a = div('a')[0]
        l = a['href']
        links.append(urlPrefix + l)
        
    return links

def GetClassLinks(url):
    ''''''
    mainUrl = url
    pageContent = Page(mainUrl).Content
    soup = BeautifulSoup(pageContent)
    
    urlPrefix = 'http://www.yeeyan.com'
    alinks = soup('table')[0].findAll('a', {'class':'bigtxt bold'})
    
    links = []
    for alink in alinks:
        links.append(urlPrefix + alink['href'])

    return links

def GetArticle(url):
    ''''''
    mainUrl = url
    pageContent = Page(mainUrl).Content
    soup = BeautifulSoup(pageContent)

    if len(soup.findAll('div', {'class':'panel'})) > 0:
        print 'File Error!'
        return '',''
    
    divs = soup('div')
    divItem = _getItemDiv(divs)

    title = divItem('h1')[0].next.next.next
    c = divItem('div', id='article_body')[0]
    rTag = re.compile(r"<[^>]*>", re.I|re.M)
    rP = re.compile(r"</p>", re.I|re.M)
    rBR = re.compile(r"<br[^>]*>", re.I|re.M)
    content = str(c).decode('utf-8')
    content = rP.sub('\r\n', content)
    content = rBR.sub('\r\n', content)
    content = rTag.sub('', content)

    return title, content

def _getItemDiv(divs):
    for div in divs:
        if div.has_key('class') and div['class'] == 'item':
            return div

if __name__ == '__main__':
    main()
