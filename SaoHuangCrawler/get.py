#!/usr/bin/env python
#coding=utf-8

# Something to get

from page import Page
from BeautifulSoup import BeautifulSoup

def main():
    ''''''
    mainUrl = 'http://www.saohuang.cn/'
    l = GetLinks(mainUrl)
    SaveLinks(l)
    print 1, 'Done!'
    
    for i in range(2, 50):
        url = 'http://www.saohuang.cn/page' + str(i) + '/'
        l = GetLinks(url)
        SaveLinks(l)
        print str(i), 'Done!'
        
def SaveLinks(links):
    f = file('output.txt', 'a')
    for i in links:
        for j in i:
            f.write(j.encode('utf-8'))
            f.write(', ')
        f.write('\r\n')


def GetLinks(url):
    ''''''
    mainUrl = url
    content = Page(mainUrl).Content
    soup = BeautifulSoup(content)

    links = []
    divs = soup('div')
    for div in divs:
        if div['class']=='diggItem':
            rank = div('a')[0].contents[0]
            title = div('h2')[0].next.next
            link = div('li')[4]('a')[0]['href']
            links.append([rank, title, link])

    return links


if __name__ == '__main__':
    main()
