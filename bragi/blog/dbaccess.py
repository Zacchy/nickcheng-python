#!/usr/bin/env python
#coding=utf-8

from django.db import connection
import sqlhelper

def getArticleIDs(page, count):
    cursor = connection.cursor()
    sql = sqlhelper.GetArticleIDs(page, count)
    cursor.execute(sql)
    ids = [row[0] for row in cursor.fetchall()]
    connection.close()
    return ids

def getArticlesByID(idList):
    cursor = connection.cursor()
    articles = []
    for id in idList:
        sql = sqlhelper.GetArticleByID(id)
        if cursor.execute(sql) == 1:
            article = Article(cursor.fetchall()[0])
            articles.append(article)
    connection.close()
    return articles

class Article:
    def __init__(self, pList):
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
