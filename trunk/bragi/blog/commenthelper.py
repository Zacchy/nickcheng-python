#!/usr/bin/env python
#coding=utf-8

def Process(commentList):
    for a in commentList:
        _processContent(a)
    return commentList
    
def _processContent(comment):
    # 把留言中的\r\n转换成<br />
    comment.Content = comment.Content.replace('\r\n','<br />')
    return comment

