#!/usr/bin/env python
#coding=utf-8

def GetArticleIDs(page, count):
    offset = (page - 1) * count
    sql = 'select ID from blog_posts order by post_date_gmt desc limit %s,%s'
    result = sql % (offset, count)
    return result

def GetArticlesByID(idList):
    sList = str(tuple(idList)).replace('L','');
    if len(sList) == 2:
        return None
    sql = 'select post_author, post_date, post_date_gmt, post_content, post_title, post_category, post_summary, post_status, comment_status, post_password, post_name, post_modified, post_modified_gmt, ping_status, post_type, comment_count from blog_posts where ID in %s'
    result = sql % (sList)
    return result

def GetArticleByID(id):
    sql = 'select post_author, post_date, post_date_gmt, post_content, post_title, post_category, post_summary, post_status, comment_status, post_password, post_name, post_modified, post_modified_gmt, ping_status, post_type, comment_count from blog_posts where ID = %s'
    result = sql % (id)
    return result

def GetArticleCount():
    sql = 'select count(*) from blog_posts'
    return sql

def save_article(article):
    sql = "insert into blog_posts (post_author, post_date, post_date_gmt, post_content, post_title, post_category, post_summary, post_status, comment_status, post_password, post_name, post_modified, post_modified_gmt, ping_status, post_type, comment_count) values (%s, '%s', '%s', '%s', '%s', %s, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %s)"
    result = sql % article.generateParam()
    return result
