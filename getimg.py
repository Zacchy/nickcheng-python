#!/usr/bin/env python
#coding=utf-8
import reimport urllibimport osimport urllib2f=urllib.urlopen("http://jphotobook.com/2005_09_11_archive.html")content=f.read()searchResult=re.findall(r'<img src="(?P<LINK>[^"]*)',content)totalNum=len(searchResult)s=0localPath='d:/abc/20050911/'for link in searchResult:	params=urllib2.urlparse.urlsplit(link)	domain=params[1]	path=params[2].replace('/','.')	filename=localPath + '_'.join([domain, path])	urllib.urlretrieve(link, filename)	s+=1	print 'Done(%d/%d): %s' % (s, totalNum, link)	