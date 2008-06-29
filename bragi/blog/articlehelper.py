#!/usr/bin/env python
#coding=utf-8

def ProcessContent(articleList):
    for a in articleList:
        c = a.Content
        #process
        c = c.replace('\r\n','<br />')
        a.Content = c
    return articleList
        