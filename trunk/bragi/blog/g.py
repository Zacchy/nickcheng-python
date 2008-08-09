#!/usr/bin/env python
#coding=utf-8
# 存放全局内容的地方

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
        self.SITE_NAME = 'Nickcheng.LOG'
        self.SITE_DESCRIPTION = '这是一个测试用的东西'
        self.SITE_DOMAINPREFIX = 'localhost:8000/blog'
        self.INDEXPAGE_ARTICLECOUNT = 7
        self.INDEXPAGE_ARTICLECOUNT_RSS = 20
        
        # varible
        self.ArticleCount = 0
        self.PageCount = 0
        # self.xxx=xxx
        
        self.Refresh()
        
    def Refresh(self):
        # process const... from db
        options = dbaccess.GetOptions()
        self.SITE_NAME = options['SITE_NAME']
        self.SITE_DESCRIPTION = options['SITE_DESCRIPTION']
        self.SITE_DOMAINPREFIX = options['SITE_DOMAINPREFIX']
        self.INDEXPAGE_ARTICLECOUNT = int(options['INDEXPAGE_ARTICLECOUNT'])
        self.INDEXPAGE_ARTICLECOUNT_RSS = int(options['INDEXPAGE_ARTICLECOUNT_RSS'])
        
        # process varibles
        self.ArticleCount = dbaccess.GetArticleCount()
        self.PageCount = self.ArticleCount / self.INDEXPAGE_ARTICLECOUNT + 1
        