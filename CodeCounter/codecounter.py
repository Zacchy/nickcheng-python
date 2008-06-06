#!/usr/bin/env python
#coding=utf-8
import os

def main():
    path = '.'
    for i in os.listdir(path):
        print i,
        if os.path.isdir(path + '\\' + i):
            print 'DIR'
        else:
            print
    return

if __name__ == '__main__':
    main()

