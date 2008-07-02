#!/usr/bin/env python
#coding=utf-8

import g

def Process(articleList):
    for a in articleList:
        _processContent(a)
        _processURL(a)
    return articleList
    
def _processContent(article):
    # 把文章中的\r\n转换成<br />
    article.Content = article.Content.replace('\r\n','<br />')
    return article

def _processURL(article):
    # 生成单篇文章的URL
    article.URL = 'http://' + g.Get().SITE_DOMAINPREFIX + '/' + str(article.PostDate).split(' ')[0].replace('-','/') + '/' + article.PostName + '/'
    return article
        