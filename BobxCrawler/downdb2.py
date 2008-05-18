#!/usr/bin/env python
#coding=utf-8

import os
import sqlite3

def main():
	# 链接数据库
	conn = sqlite3.connect('all.db')
	c = conn.cursor()

	# 常量值
	loop = 10
	size = 100
	ran = 30000

	for i in range(loop):
		sql = 'select id,link from girl where status = 0 and id < %d order by id desc limit %d;' % (ran, size)
		c.execute(sql)
		for (id,link) in c.fetchall():
			print id,link
			r1 = link.rindex('/')
			r2 = link[:r1].rindex('/')
			name = link[r2+1:r1]
			fn = link[r1+1:]
			if not os.path.exists(name):    # 如果目录不存在, 则建立之
				os.mkdir(name)
			cmd = 'curl\\curl.exe -A "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)" -o %s\\%s %s' % (name, fn, link)
			os.system(cmd)
			s = 'update girl set status = 1 where id = %d;' % id
			c.execute(s)
			conn.commit()

if __name__ == '__main__':
    main()

