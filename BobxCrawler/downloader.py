#!/usr/bin/env python
#coding=utf-8

import os

def main():
    # 获取txt目录下文件列表
    fileList = []
    for r, d, f in os.walk('txt\\'):
        for ff in f:
            fileList.append(ff)

    for tf in fileList:
        print tf
        name = tf[:tf.index('.')]
        if not os.path.exists(name):    # 如果目录不存在, 则建立之
            os.mkdir(name)

        links = []
        f = open('txt\\'+tf,'r')
        all = f.read()

        for line in all.split('\r\n'):
            if line == '':
                continue
            fn = line[line.rindex('/')+1:]
            cmd = 'curl\\curl.exe -A "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)" -o %s\\%s %s' % (name, fn, line)
            os.system(cmd)

if __name__ == '__main__':
    main()

