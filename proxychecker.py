import urllib
from HTMLParser import HTMLParser
#from string import letters
import time

#import pprint

def parserhtmllist(htmldata):
	class MyHTMLParser (HTMLParser):
		def set(self): 
			self.S = 'none'
			self.I = []
			self.l = 0
		def handle_starttag(self, tag, attrs):
			if ('class', 'cells') in attrs and tag == 'tr':
				self.l = 0
				self.S = 'cell'
				self.I.append([])
			if self.S == 'cell' and tag == 'td':
				self.l += 1
				self.S = 'celltd'
		def handle_endtag(self, tag):
			if self.S == 'celltd' and tag == 'td':
				self.l -= 1
				if self.l == 0:
					self.S = 'cell'
				if self.S == 'cell' and tag == 'tr':
					self.S = 'none'
		def handle_data(self, data):
			if self.S == 'celltd' and self.l >= 1:
				self.I[-1].append(data)
		def getlist(self):
			I = []
			for x in self.I:
				try:
					int(x[0])
					I.append((x[1], x[2]))
				except:
					pass
			return I

	p = MyHTMLParser()
	p.set()
	p.feed(htmldata)
	p.close()
	return p.getlist()

def getproxylist(proxylisturl, testurls, proxies = {}, maxtime = 20, debug = True):
	opener = urllib.FancyURLopener(proxies)
	data = opener.open(proxylisturl).read()
	I = parserhtmllist(data)
	TI = []
	for server, port in I:
		proxy = {'htt': 'http://%s:%s' % (server, port)}
		opener = urllib.FancyURLopener(proxies)
		TI.append([])
		if debug:
			print 'testing %s:%s' % (server, port)
		for url in testurls:
			try:
				st = time.time()
				filehandle = opener.open(url)
				et = time.time()
				TI[-1].append(et - st)
			except IOError:
				TI[-1].append(maxtime)
	return zip(I, TI)

if __name__ == '__main__':
	 proxylisturl = 'http://www.haozs.net/proxyip/index.php?act=list&port=&type=&country=China&page=1'
	 testurls = ['http://www.google.com']

	 M = getproxylist(proxylisturl, testurls)
	 M.sort(key = lambda x: sum(x[1]))

	 print '\nResult(sorted):'
	 for x in M:
		 print '%s:%s\t%g' % (x[0][0], x[0][1], sum(x[1]))
	
