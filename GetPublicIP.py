#coding=utf-8
import urllib
import re
import libgmail
import time

# Get the page content
url = 'http://admin:Anywhere4@192.168.0.1/status.htm'
data = urllib.urlopen(url)
pageContent = data.read()

# Filter & Get the IP
begin = pageContent.find('IP µÿ÷∑', 3000)+21
end = pageContent.find('&', begin)
IP = pageContent[begin: end - 1]

# Get current time
t = time.localtime()
datetime = "-".join([str(a) for a in t[:3]]) + ' ' + ":".join([str(a) for a in t[3:6]])

# Generate content
content = IP + ' - ' + datetime

# Send mail
ga = libgmail.GmailAccount("nick.nickcheng@gmail.com", "1738517385")
gcm = libgmail.GmailComposedMessage('nick.nickcheng@gmail.com', 'HOME IP', content)
ga.login()
ga.sendMessage(gcm)

print "Done!"

