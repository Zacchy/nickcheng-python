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

def GetCommentIDs(id):
    cursor = connection.cursor()
    sql = sqlhelper.GetCommentIDs(id)
    cursor.execute(sql)
    ids = [row[0] for row in cursor.fetchall()]
    connection.close()
    return ids

def GetCommentsByID(idList):
    cursor = connection.cursor()
    comments = []
    for id in idList:
        sql = sqlhelper.GetCommentByID(id)
        if cursor.execute(sql) == 1:
            comment = Comment(pList = cursor.fetchall()[0])
            comments.append(comment)
    connection.close()
    return comments
    

class Article:
    def __init__(self, title='', slug='', content='', pList=[]):
        self.AutherID = -1
        self.PostDate = time.strftime('%Y-%m-%d %X')
        self.PostDateGMT = time.strftime('%Y-%m-%d %X',time.gmtime())
        self.Content = ''
        self.Title = ''
        self.Category = 0
        self.Summary = ''
        self.Status = 'publish'
        self.CommentStatus = 'open'
        self.Password = ''
        self.PostName = ''
        self.ModifiedDate = self.PostDate
        self.ModifiedDateGMT = self.PostDateGMT
        self.PingStatus = 'open'
        self.PostType = 'post'
        self.CommentCount = 0
        self.ID = -1
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
            self.ID = pList[16]
        else:
            self.Title = title
            self.PostName = slug
            self.Content = content
    
    def generateParam(self):
        return (self.AutherID, self.PostDate, self.PostDateGMT, self.Content, self.Title, self.Category, self.Summary, self.Status, self.CommentStatus, self.Password, self.PostName, self.ModifiedDate, self.ModifiedDateGMT, self.PingStatus, self.PostType, self.CommentCount)
    
class Comment:
    def __init__(self, postid=-1, author='', authoremail='', authorurl='', authorip='', content='', agent='', userid=0, pList=[]):
        self.ID = -1
        self.PostID = -1
        self.Author = ''
        self.AuthorEmail = ''
        self.AuthorURL = ''
        self.AuthorIP = ''
        self.PostDate = time.strftime('%Y-%m-%d %X')
        self.PostDateGMT = time.strftime('%Y-%m-%d %X',time.gmtime())
        self.Content = ''
        self.Approved = 1
        self.Agent = ''
        self.Type = ''
        self.UserID = 0
        
        if pList:
            self.ID = pList[0]
            self.PostID = pList[1]
            self.Author = pList[2]
            self.AuthorEmail = pList[3]
            self.AuthorURL = pList[4]
            self.AuthorIP = pList[5]
            self.PostDate = pList[6]
            self.PostDateGMT = pList[7]
            self.Content = pList[8]
            self.Approved = pList[9]
            self.Agent = pList[10]
            self.Type = pList[11]
            self.UserID = pList[12]
        else:
            self.PostID = postid
            self.Author = author
            self.AuthorEmail = authoremail
            self.AuthorURL = authorurl
            self.AuthorIP = authorip
            self.Content = content
            self.Agent = agent
            self.UserID = userid
            
    def generateParam(self):
        return (self.PostID, self.Author, self.AuthorEmail, self.AuthorURL, self.PostDate, self.PostDateGMT, self.Content, self.Approved, self.Agent, self.Type, self.UserID)
            