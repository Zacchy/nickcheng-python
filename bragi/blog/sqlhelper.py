#!/usr/bin/env python
#coding=utf-8

def GetArticleIDs(page, count):
    offset = (page - 1) * count
    sql = 'select ID from blog_posts order by post_date_gmt desc limit %s,%s'
    result = sql % (offset, count)
    return result

def GetArticleID(year, month, day, slug):
    date = '-'.join((year, month, day))
    sql = "select ID from blog_posts where post_date >= '%s' and post_name = '%s'"
    result = sql % (date, slug)
    return result

def GetArticlesByID(idList):
    sList = str(tuple(idList)).replace('L','');
    if len(sList) == 2:
        return None
    sql = 'select post_author, post_date, post_date_gmt, post_content, post_title, post_category, post_summary, post_status, comment_status, post_password, post_name, post_modified, post_modified_gmt, ping_status, post_type, comment_count, ID from blog_posts where ID in %s'
    result = sql % (sList)
    return result

def GetArticleByID(id):
    sql = 'select post_author, post_date, post_date_gmt, post_content, post_title, post_category, post_summary, post_status, comment_status, post_password, post_name, post_modified, post_modified_gmt, ping_status, post_type, comment_count, ID from blog_posts where ID = %s'
    result = sql % (id)
    return result

def GetArticleCount():
    sql = 'select count(*) from blog_posts'
    return sql

def save_article(article):
    sql = "insert into blog_posts (post_author, post_date, post_date_gmt, post_content, post_title, post_category, post_summary, post_status, comment_status, post_password, post_name, post_modified, post_modified_gmt, ping_status, post_type, comment_count) values (%s, '%s', '%s', '%s', '%s', %s, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %s)"
    result = sql % article.generateParam()
    return result

def GetCommentIDs(id):
    sql = 'select comment_ID from blog_comments where comment_post_ID = %s order by comment_date_gmt desc'
    result = sql % (id)
    return result
    
def GetCommentByID(id):
    sql = 'select comment_ID, comment_post_ID, comment_author, comment_author_email, comment_author_url, comment_author_IP, comment_date, comment_date_gmt, comment_content, comment_approved, comment_agent, comment_type, user_id from blog_comments where comment_ID = %s'
    result = sql % (id)
    return result
    