#!/usr/bin/env python
#coding=utf-8

from django.db import connection
from django.db import transaction
import time

import sqlhelper

def GetArticleIDs(page, count):
    cursor = connection.cursor()
    sql = sqlhelper.GetArticleIDs(page, count)
    cursor.execute(sql)
    ids = [row[0] for row in cursor.fetchall()]
    connection.close()
    return ids

def GetArticleID(year, month, day, slug):
    cursor = connection.cursor()
    sql = sqlhelper.GetArticleID(year, month, day, slug)
    cursor.execute(sql)
    id = [row[0] for row in cursor.fetchall()]
    connection.close()
    return id

def GetArticlesByID(idList):
    cursor = connection.cursor()
    articles = []
    for id in idList:
        sql = sqlhelper.GetArticleByID(id)
        if cursor.execute(sql) == 1:
            article = Article(pList = cursor.fetchall()[0])
            articles.append(article)
    connection.close()
    return articles

def GetArticleCount():
    cursor = connection.cursor()
    sql = sqlhelper.GetArticleCount()
    cursor.execute(sql)
    count = [row[0] for row in cursor.fetchall()][0]
    connection.close()
    return count

@transaction.commit_manually
def save_article(title, slug, content):
    cursor = connection.cursor()
    article = Article(title = title, slug = slug, content = content)
    sql = sqlhelper.save_article(article)
    cursor.execute(sql)
    transaction.commit()
    connection.close()
    return article

class Article:
    def __init__(self, title='', slug='', content='', pList=[]):
        self.AutherID = -1
        self.PostDate = time.strftime('%Y-%m-%d %X')
        self.PostDateGMT = time.strftime('%Y-%m-%d %X',time.gmtime())
        self.Content = ''
        self.Title = ''
        self.Category = -1
        self.Summary = ''
        self.Status = ''
        self.CommentStatus = ''
        self.Password = ''
        self.PostName = ''
        self.ModifiedDate = self.PostDate
        self.ModifiedDateGMT = self.PostDateGMT
        self.PingStatus = ''
        self.PostType = ''
        self.CommentCount = 0
        #
        self.URL = ''
        
        if pList:
            self.AutherID = pList[0]
            self.PostDate = pList[1]
            self.PostDateGMT = pList[2]
            self.Content = pList[3]
            self.Title = pList[4]
            self.Category = pList[5]
            self.Summary = pList[6]
            self.Status = pList[7]
            self.CommentStatus = pList[8]
            self.Password = pList[9]
            self.PostName = pList[10]
            self.ModifiedDate = pList[11]
            self.ModifiedDateGMT = pList[12]
            self.PingStatus = pList[13]
            self.PostType = pList[14]
            self.CommentCount = pList[15]
        else:
            self.Title = title
            self.PostName = slug
            self.Content = content
    
    def generateParam(self):
        return (self.AutherID, self.PostDate, self.PostDateGMT, self.Content, self.Title, self.Category, self.Summary, self.Status, self.CommentStatus, self.Password, self.PostName, self.ModifiedDate, self.ModifiedDateGMT, self.PingStatus, self.PostType, self.CommentCount)