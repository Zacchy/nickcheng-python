#!/usr/bin/env python
#coding=utf-8
# 存放全局内容的地方

SITE_DOMAINPREFIX = 'localhost:8000'

INDEXPAGE_ARTICLECOUNT = 7 # 首页的文章数量

import dbaccess
_settings = None

def Get():
    global _settings
    if not _settings:
        _settings = Settings()
    return _settings

class Settings():
    def __init__(self):
        # const
        self.SITE_DOMAINPREFIX = 'localhost:8000/blog'
        self.INDEXPAGE_ARTICLECOUNT = 7
        # varible
        self.ArticleCount = 0
        self.PageCount = 0
        # self.xxx=xxx
        
        self.Refresh()
        
    def Refresh(self):
        self.ArticleCount = dbaccess.GetArticleCount()
        self.PageCount = self.ArticleCount / self.INDEXPAGE_ARTICLECOUNT + 1
        