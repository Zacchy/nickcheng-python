#!/usr/bin/env python
#coding=utf-8

# 业务层代码. 供View调用, 主要进行一些业务逻辑的封装
# 本层主要调用dbaccess层

import dbaccess
import g
import urlhelper

def GetArticles(page):
    '''
    获取指定页的文章
    '''
    articleCount = g.Get().INDEXPAGE_ARTICLECOUNT
    articleIDs = dbaccess.GetArticleIDs(page, articleCount)
    articles = dbaccess.GetArticlesByID(articleIDs)
    return articles

def GetPager(pageNo):
    '''
    获取每页下方的"前一页","后一页"
    '''
    pagerLinks = []
    if pageNo > g.Get().PageCount:
        return None
    elif pageNo == 1:
        pagerLinks.append(['<<老文章', urlhelper.IndexURL(pageNo + 1)])
    elif pageNo == g.Get().PageCount:
        pagerLinks.append(['新文章>>', urlhelper.IndexURL(pageNo - 1)])
    else:
        pagerLinks.append(['<<老文章', urlhelper.IndexURL(pageNo + 1)])
        pagerLinks.append(['新文章>>', urlhelper.IndexURL(pageNo - 1)])
    return pagerLinks