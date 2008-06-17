#!/usr/bin/env python
#coding=utf-8

# 业务层代码. 供View调用, 主要进行一些业务逻辑的封装
# 本层主要调用dbaccess层

import dbaccess
import g

def getArticles(page):
    '''
    获取指定页的文章
    '''
    articleCount = g.INDEXPAGE_ARTICLECOUNT
    articleIDs = dbaccess.getArticleIDs(page, articleCount)
    articles = dbaccess.getArticlesByID(articleIDs)
    return articles

