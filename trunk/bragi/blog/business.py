#!/usr/bin/env python
#coding=utf-8

# 业务层代码. 供View调用, 主要进行一些业务逻辑的封装
# 本层主要调用dbaccess层

import dbaccess
import g
import urlhelper
import articlehelper

def GetArticles(page, pageSize = None):
    '''
    获取指定页的文章
    '''
    if not pageSize:
        pageSize = g.Get().INDEXPAGE_ARTICLECOUNT
    articleIDs = dbaccess.GetArticleIDs(page, pageSize)
    articles = dbaccess.GetArticlesByID(articleIDs)
    return articlehelper.Process(articles)

def GetArticle(year, month, day, slug):
    '''
    获取指定的文章
    '''
    articleID = dbaccess.GetArticleID(year, month, day, slug)
    article = dbaccess.GetArticlesByID(articleID)[0]
    return articlehelper.Process([article])[0]

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

def save_article(title, slug, content):
    if ' ' in slug:
        slug = slug.replace(' ', '-')
    dbaccess.save_article(title, slug, content)
    
def Articles2RSS(articleList):
    from django.utils import feedgenerator
    f = feedgenerator.Atom1Feed(
        title = g.Get().SITE_NAME,
        link = 'http://' + g.Get().SITE_DOMAINPREFIX,
        description = g.Get().SITE_DESCRIPTION,
        language = 'zh-cn',
        author_email = '',
        author_name = '',
        author_link = '',
        subtitle = '',
        categories = '',
        feed_url = '',
        feed_copyright = ''
    )
    for at in articleList:
        f.add_item(
            title = at.Title,
            link = at.URL,
            description = at.Content,
            author_email = None,
            author_name = None,
            author_link = None,
            pubdate = at.PostDate,
            comments = at.URL + '#comments',
            unique_id = None,
            enclosure = None,
            categories = (),
            item_copyright = None
        )
        print at.PostDate
    return f