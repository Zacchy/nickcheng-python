#!/usr/bin/env python

"""
Merger for msnlib logfiles.

It takes two logfiles as arguments, and prints out the merge between them,
sorting using the time.

Quite useful when you have used msn in two different places and want to unify
the logs.


Note that this will not do absolute time sorting (as it's usual for time to go
backwards, as we all know =), but record-by-record time compares.

Alberto Bertogli (albertogli@telpin.com.ar), 02/Jun/2003
Please send any reports to msnlib-devel@auriga.wearlab.de.
"""


import sys
import time


def get_records(fd):
	records = []
	l = fd.readline()
	rec = l
	l = fd.readline()
	while rec:
		# if the line begins with \t, then it's a multi-line record
		if l and l[0] == '\t':
			rec += l
			l = fd.readline()
			continue
		
		# process the actual record
		ls = rec.split(' ', 2)
		raw_date = ls[0] + ' ' + ls[1]
		date = time.strptime(raw_date, '%d/%b/%Y %H:%M:%S ')
		date = time.mktime(date)
		records.append((date, rec))
		
		# save the current line
		rec = l
		l = fd.readline()
	return records

def panic(s):
	print s
	sys.exit(1)

try:
	fd1 = open(sys.argv[1])
	fd2 = open(sys.argv[2])
except:
	panic("Use: hmerge file1 file2")

# this is the invalid record to mark the end of the record list
eor_record = (0, '')


rec1 = get_records(fd1)
rec2 = get_records(fd2)

if not rec1: panic("Error: file 1 doesn't have any records")
if not rec2: panic("Error: file 1 doesn't have any records")

# append the eor_record to both lists
rec1.append(eor_record)
rec2.append(eor_record)

len1 = len(rec1)
len2 = len(rec2)

point1 = 0
point2 = 0

while 1:
		
	r1 = rec1[point1]
	r2 = rec2[point2]
	
	# if we have any at the end, print it or exit
	if r1[0] == 0 or r2[0] == 0:
		# if we reach the end of both lists, we exit
		if r1[0] == 0 and r2[0] == 0:
			break
		if r1[0] == 0:
			print r2[1],
			point2 += 1
		elif r2[0] == 0:
			print r1[1],
			point1 += 1
	
	# otherwise, compare and print the earlier
	else:
		if r1[0] < r2[0]:
			print r1[1],
			point1 += 1
		elif r1[0] > r2[0]:
			print r2[1],
			point2 += 1
		else:
			print r1[1],
			print r2[1],
			point1 += 1
			point2 += 1
		

