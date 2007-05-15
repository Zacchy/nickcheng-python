#!/usr/bin/env python
#coding=utf-8

"""
This is a very simple bot to show how automation using msnlib could be done.
It's not quite useful as-is, but provides a good example.

If you play with it, please let me know.
"""


# sys, for getting the parameters
import sys

# time, for sleeping
import time

# select to wait for events
import select

# socket, to catch errors
import socket

# thread, for creating the worker thread
import thread

# and, of course, msnlib
import msnlib
import msncb


m = msnlib.msnd()
m.cb = msncb.cb()


def do_work():
	"""
	Here you do your stuff and send messages using m.sendmsg()
	This is the only place your code lives
	"""
	
	# wait a bit for everything to settle down (sync taking efect
	# basically)
	time.sleep(15)
	
	print '-' * 20 + 'SEND 1'
	print m.sendmsg("nickcheng@live.com", "帅哥")

	print '-' * 20 + 'SEND 2'
	print m.sendmsg("nickcheng@live.com", "你好")

	# give time to send the messages
	time.sleep(30)

	# and then quit
	quit()
	

# you shouldn't need to touch anything past here


# get the login email and password from the parameters
try:
	m.email = 'chengnick@hotmail.com'
	m.pwd = '1738517385'
except:
	print "Use: msnbot email password"
	sys.exit(1)


print "Logging In"
m.login()

print "Sync"
# this makes the server send you the contact list, and it's recommended that
# you do it because you can get in trouble when getting certain events from
# people that are not on your list; and it's not that expensive anyway
m.sync()

print "Changing Status"
# any non-offline status will do, otherwise we'll get an error from msn when
# sending a message
m.change_status("away")

def quit():
	try:
		m.disconnect()
	except:
		pass
	print "Exit"
	sys.exit(0)

# we start a thread to do the work. it's a thread because we want to share
# everything, and fork cow semantics cause problems here
#thread.start_new_thread(do_work, ())


# we loop over the network socket to get events
print "Loop"
while 1:
	# we get pollable fds
	t = m.pollable()
	infd = t[0]
	outfd = t[1]

	# we select, waiting for events
	try:
		fds = select.select(infd, outfd, [], 0)
	except:
		quit()
	
	for i in fds[0] + fds[1]:       # see msnlib.msnd.pollable.__doc__
		try:
			m.read(i)
		except ('SocketError', socket.error), err:
			if i != m:
				# user closed a connection
				# note that messages can be lost here
				m.close(i)
			else:
				# main socket closed
				quit()

	# sleep a bit so we don't take over the cpu
	time.sleep(0.01)



