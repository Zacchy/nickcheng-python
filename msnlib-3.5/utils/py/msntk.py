#!/usr/bin/env python

import sys
import time
import string
import socket
import select
from Tkinter import *
import tkMessageBox
import tkSimpleDialog

import msnlib
import msncb

"""
MSN Tk Client

This is a beta msn client based on msnlib. As you see, it's GUI based on the
Tk bindings, which provide an abstraction to create graphical interfaces; it
works both under linux, windows and probably others too.

For further information refer to the documentation or the source (which is
always preferred).
Please direct any comments to the msnlib mailing list,
msnlib-devel@auriga.wearlab.de.
You can find more information, and the package itself, at
http://users.auriga.wearlab.de/~alb/msnlib
"""


# main msnlib classes
m = msnlib.msnd()
m.cb = msncb.cb()

# void debug output
#def void(s): pass
#msnlib.debug = msncb.debug = void



#
# useful functions
#

#sys.setdefaultencoding("iso-8859-15")
encoding = 'iso-8859-1'

def encode(s):
	try:
		return s.decode(encoding).encode('utf-8')
	except:
		return s

def decode(s):
	try:
		return s.decode('utf-8').encode(encoding)
	except:
		return s

def nick2email(nick):
	"Returns an email according to the given nick, or None if noone matches"
	for email in m.users.keys():
		if str(m.users[email].nick) == str(nick):
			return email
	if nick in m.users.keys():
		return nick
	return None

def email2nick(email):
	"Returns a nick accoriding to the given email, or None if noone matches"
	if email in m.users.keys():
		return m.users[email].nick
	else:
		return None

def now():
	"Returns the current time in format HH:MM:SSTT"
	return time.strftime('%I:%M:%S%p', time.localtime(time.time()) )

def quit():
	"Cleans up and quits everything"
	try:
		m.disconnect()
	except:
		pass
	root.quit()
	sys.exit(0)



#
# GUI classes
#

class userlist(Frame):
	"The user list"
	def __init__(self, master):
		Frame.__init__(self, master)
		self.scrollbar = Scrollbar(self, orient = VERTICAL)
		self.list = Listbox(self, 
				yscrollcommand = self.scrollbar.set)
		self.list.config(font = "Courier")
		self.scrollbar.config(command = self.list.yview)
		self.scrollbar.pack(side = RIGHT, fill = Y)
		self.list.pack(side = LEFT, fill = BOTH, expand = 1)
		
		self.list.bind("<Double-Button-1>", self.create_chat)
			
	def create_chat(self, evt = None):
		"Creates a chat window"
		if m.status == 'HDN':
			tkMessageBox.showwarning("Warning", 
				"You can't open chats when you're invisible")
			return
		nick = self.list.get(self.list.curselection())[4:]
		email = nick2email(nick)
		if email in emwin.keys():
			emwin[email].lift()
		elif m.users[email].status == 'FLN':
			tkMessageBox.showwarning("Warning",
				"The user is offline")
		else:
			emwin[email] = chatwindow(root, email)
	

class mainmenu(Menu):
	"Main menu used in the main window"
	def __init__(self, master):
		Menu.__init__(self, master)
		self.status_menu = Menu(self, tearoff = 0)
		self.add_cascade(label = "Status", menu = self.status_menu)
		self.status_menu.add_command(label = "Online",
			command = self.chst_online)
		self.status_menu.add_command(label = "Away",
			command = self.chst_away)
		self.status_menu.add_command(label = "Busy",
			command = self.chst_busy)
		self.status_menu.add_command(label = "Be Right Back",
			command = self.chst_brb)
		self.status_menu.add_command(label = "Lunch",
			command = self.chst_lunch)
		self.status_menu.add_command(label = "Phone", 
			command = self.chst_phone)
		self.status_menu.add_command(label = "Invisible", 
			command = self.chst_invisible)
			
		self.add_command(label = 'Info', command = self.show_info)
	
	def show_info(self, evt = None):
		csel = mainlist.list.curselection()
		if not csel:
			return
		nick = mainlist.list.get(csel)[4:]
		email = nick2email(nick)
		infowindow(root, email)

	# status change callbacks
	def clear_heads(self):
		for i in emwin.keys():
			emwin[i].head.config(text = '')
	
	def chst_online(self):
		self.clear_heads()
		m.change_status('online')
	def chst_away(self):
		self.clear_heads()
		m.change_status('away')
	def chst_busy(self):
		self.clear_heads()
		m.change_status('busy')
	def chst_brb(self):
		self.clear_heads()
		m.change_status('brb')
	def chst_lunch(self):
		self.clear_heads()
		m.change_status('lunch')
	def chst_phone(self):
		self.clear_heads()
		m.change_status('phone')
	def chst_invisible(self):
		warn = "Warning: as you are invisible, it is possible that\n"
		warn += "the messages you type here never get to the user."
		for i in emwin.keys():
			emwin[i].head.config(text = warn)
		m.change_status('invisible')


class chatwindow(Toplevel):
	"Represents a chat window"
	def __init__(self, master, email):
		Toplevel.__init__(self, master)
		self.email = email
		self.protocol("WM_DELETE_WINDOW", self.destroy_window)
		nick = email2nick(email)
		# FIXME: update the title with status change
		status = msnlib.reverse_status[m.users[email].status]
		if nick:
			self.wm_title(nick + ' (' + status + ')')
		else:
			self.wm_title(email + ' (' + status + ')')

		# head label
		self.head = Label(self)
		self.head.pack(side = TOP, fill = X, expand = 0)
		self.head.config(justify = LEFT)
		self.head.config(text = "")

		# text box (with scrollbar), where the message goes
		self.frame = Frame(self)
		self.scrollbar = Scrollbar(self.frame, orient = VERTICAL)
		self.text = Text(self.frame, 
				yscrollcommand = self.scrollbar.set)
		self.scrollbar.config(command = self.text.yview)
		self.scrollbar.pack(side = RIGHT, fill = Y)
		self.text.pack(side = TOP, fill = BOTH, expand = 1)
		self.frame.pack(side = TOP, fill = BOTH, expand = 1)
		
		self.text.config(state = DISABLED)
		self.text.tag_config('from', foreground = 'blue')
		self.text.tag_config('to', foreground = 'red')
		self.text.tag_config('typing', foreground = 'lightblue')
		
		# entry, where the user types
		self.entry = Entry(self)
		self.entry.pack(side = BOTTOM, fill = X, expand = 0)
		self.entry.bind('<Return>', self.send_line)
	
	def append(self, s, direction, scroll = 1):
		"Adds text to the window's text box"
		self.text.config(state = NORMAL)
		self.text.insert(END, s, direction)
		self.text.yview(SCROLL, scroll, UNITS)
		self.text.config(state = DISABLED)
	
	def send_line(self, evt = None):
		"Sends the current entry as a message"
		msg = self.entry.get()
		lines = msg.split('\n')
		if len(lines) == 1:
			s = now() + ' >>> ' + msg + '\n'
		else:
			s = now() + ' >>>\n\t'
			s += string.join(lines, '\n\t')
			s = s[:-1]
		self.append(s, 'to', scroll = len(lines))
		
		# we need to encode it before sending because msg is already
		# an unicode string; so use utf-8
		msg = msg.encode('utf-8')

		m.sendmsg(self.email, msg)
		self.entry.delete(0, END)
	
	def destroy_window(self, evt = None):
		"Clean up when the window is closed"
		del(emwin[self.email])
		self.destroy()


class infowindow(Toplevel):
	"Represents a window with user information"
	def __init__(self, master, email):
		Toplevel.__init__(self, master)
		self.email = email
		self.wm_title('Info on ' + email)
		u = m.users[email]
		out = ''
		out += 'Information for user ' + email + '\n\n'
		out += 'Nick: ' + u.nick + '\n'
		out += 'Status: ' + msnlib.reverse_status[u.status] + '\n'
		if 'B' in u.lists:
			out += 'Mode: ' + 'blocked' + '\n'
		if u.gid != None:
			out += 'Group: ' + m.groups[u.gid] + '\n'
		if u.realnick:
			out += 'Real Nick: ' + u.realnick + '\n'
		if u.homep:
			out += 'Home phone: ' + u.homep + '\n'
		if u.workp:
			out += 'Work phone: ' + u.workp + '\n'
		if u.mobilep:
			out += 'Mobile phone: ' + u.mobilep + '\n'

		self.label = Label(self)
		self.label.pack(side = TOP, fill = BOTH, expand = 1)
		self.label.config(justify = LEFT)
		self.label.config(text = out)


def redraw_main():
	"Redraws the main screen"
	# sync the user list - FIXME: instead of redrawing, use the callbacks
	# for status change notifications
	nicks = []
	for i in m.users.keys():
		if m.users[i].status == 'FLN':
			s = '[X] '
		elif m.users[i].status in ('NLN', 'IDL'):
			s = '[ ] '
		else:
			s = '[-] '
		if 'B' in m.users[i].lists:
			s = '[!] '
		
		s += m.users[i].nick
		nicks.append(s)
	nicks.sort()
	mainlist.list.delete(0, END)
	for i in nicks:
		mainlist.list.insert(END, i)
	
	# update status
	s = msnlib.reverse_status[m.status]
	status.config(text = s)



#
# callbacks
#

def cb_msg(md, type, tid, params, sbd):
	"Gets a message"
	t = tid.split(' ')
	email = t[0]

	# parse
	lines = params.split('\n')
	headers = {} 
	eoh = 0
	for i in lines:
		# end of headers
		if i == '\r':
			break
		tv = i.split(':', 1)
		type = tv[0]
		value = tv[1].strip()
		headers[type] = value
		eoh += 1
	eoh +=1

	# ignore hotmail messages
	if email == 'Hotmail':
		return
	
	if email not in emwin.keys():
		emwin[email] = chatwindow(root, email)
		
	# typing notifications
	if (headers.has_key('Content-Type') and 
			headers['Content-Type'] == 'text/x-msmsgscontrol'):
		if not m.users[email].priv.has_key('typing'):
			m.users[email].priv['typing'] = 1
			msg = now() + ' --- is typing\n'
			emwin[email].append(msg, 'typing')
			
	# normal message
	else:
		if len(lines[eoh:]) > 1:
			msg = now() + ' <<<\n\t'
			msg += string.join(lines[eoh:], '\n\t')
			msg = msg.replace('\r', '')
		else:
			msg = now() + ' <<< ' + lines[eoh] + '\n'
			
		if m.users[email].priv.has_key('typing'):
			del(m.users[email].priv['typing'])
			
		emwin[email].append(msg, 'from')
		root.bell()

	msncb.cb_msg(md, type, tid, params, sbd)
m.cb.msg = cb_msg



#
# main
#

# email - chatwindow dictionary
emwin = {}

# gui init
root = Tk()
root.wm_title('msnlib')

mainlist = userlist(root)
mainlist.pack(side = TOP, fill = BOTH, expand = 1)

status = Label(root, text = "logging in...", bd=1, relief = SUNKEN, anchor = W)
status.pack(side = BOTTOM, fill = X, expand = 0)

menu = mainmenu(root)
root.config(menu = menu)

# initial update, to display at least something while we log in
root.update()

# ask for username and password if not given in the command line
if len(sys.argv) < 3:
	m.email = tkSimpleDialog.askstring("Username",
		"Please insert your email")
	if not m.email:
		quit()
	
	m.pwd = tkSimpleDialog.askstring("Password",
		"Please insert your password")
	if not m.pwd:
		quit()
else:
	m.email = sys.argv[1]
	m.pwd = sys.argv[2]

m.email = m.email.strip()
m.pwd = m.pwd.strip()

# the encoding is utf-8 because the text class uses unicode directly
m.encoding = 'utf-8'

root.update()

# login
try:
	m.login()
	m.sync()
except 'AuthError':
	tkMessageBox.showerror("Login", "Error logging in: wrong password")
	quit()

# start as invisible
m.change_status('invisible')


# main loop
while 1:
	fds = m.pollable()
	infd = fds[0]
	outfd = fds[1]
	
	try:
		# both network and gui checks
		fds = select.select(infd, outfd, [], 0)
		root.update()
	except KeyboardInterrupt:
		quit()
	except TclError:
		quit()

	for i in fds[0] + fds[1]:
		try:
			m.read(i)
		except ('SocketError', socket.error), err:
			if i != m:
				m.close(i)
			else:
				tkMessageBox.showwarning("Warning",
					"Server disconnected us - you " +
					"probably logged in somewhere else")
				quit()
		
		# always redraw after a network event
		redraw_main()
	
	# sleep a bit so we don't take over the cpu
	time.sleep(0.05)


