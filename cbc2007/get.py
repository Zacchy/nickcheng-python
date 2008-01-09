#!/usr/bin/env python
#coding=utf-8

# Something to get

from page import Page
from BeautifulSoup import BeautifulSoup

def main():
    ''''''
    mainUrl = 'http://events.cnbloggercon.org/event/cnbloggercon2007/'
    content = Page(mainUrl).Content
    soup = BeautifulSoup(content)
    
    links = soup('a')
    peopleList = []
    for item in links:
        href = item['href']
        if href.lower()[:8] == '/people/':
            peopleList.append('http://events.cnbloggercon.org' + href + 'profile/')

    pageLink = []
    for link in peopleList:
        print link
        ct = Page(str(link.encode('utf-8')).lower()).Content
        pos = ct.find('个人网站')
        if pos == -1:
            continue
        ct = ct[pos:]
        so = BeautifulSoup(ct)
        fLink = so('a')[0]['href']
        pageLink.append(fLink)

    f = file('abcde.txt', 'w')
    for i in pageLink:
        f.write(i)
        f.write('\r\n')

if __name__ == '__main__':
    main()
