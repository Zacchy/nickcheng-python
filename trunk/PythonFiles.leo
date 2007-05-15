<?xml version="1.0" encoding="utf-8"?>
<?xml-stylesheet ekr_test?>
<leo_file>
<leo_header file_format="2" tnodes="0" max_tnode_index="0" clone_windows="0"/>
<globals body_outline_ratio="0.355515041021">
	<global_window_position top="10" left="10" height="762" width="1097"/>
	<global_log_window_position top="0" left="0" height="0" width="0"/>
</globals>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="nickcheng.20070126145908" a="E"><vh>NewHeadline</vh>
<v t="nickcheng.20070126145908.1"><vh>@thin abc.txt</vh></v>
<v t="nickcheng.20070126184322" tnodeList="nickcheng.20070126184322"><vh>@nosent 122.txt</vh></v>
<v t="nickcheng.20070126175658" a="E"><vh>2000</vh>
<v t="nickcheng.20070126181144" a="TV"><vh>&lt;&lt; Jul &gt;&gt;</vh></v>
</v>
<v t="nickcheng.20070126171343" tnodeList="nickcheng.20070126171343"><vh>@file def.txt</vh></v>
</v>
<v t="nickcheng.20070126145908.2" a="E"><vh>@file E:/Work/Code/Python/proxychecker.py</vh>
<v t="nickcheng.20070126145908.3"><vh>&lt;&lt; proxychecker declarations &gt;&gt;</vh></v>
<v t="nickcheng.20070126145908.4"><vh>parserhtmllist</vh></v>
<v t="nickcheng.20070126145908.5"><vh>getproxylist</vh></v>
</v>
</vnodes>
<tnodes>
<t tx="nickcheng.20070126145908"></t>
<t tx="nickcheng.20070126145908.2">@ignore
@language python
&lt;&lt; proxychecker declarations &gt;&gt;
@others

if __name__ == '__main__':
	 proxylisturl = 'http://www.haozs.net/proxyip/index.php?act=list&amp;port=&amp;type=&amp;country=China&amp;page=1'
	 testurls = ['http://www.google.com']

	 M = getproxylist(proxylisturl, testurls)
	 M.sort(key = lambda x: sum(x[1]))

	 print '\nResult(sorted):'
	 for x in M:
		 print '%s:%s\t%g' % (x[0][0], x[0][1], sum(x[1]))
	
</t>
<t tx="nickcheng.20070126145908.3">import urllib
from HTMLParser import HTMLParser
#from string import letters
import time

#import pprint

</t>
<t tx="nickcheng.20070126145908.4">def parserhtmllist(htmldata):
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
			if self.S == 'celltd' and self.l &gt;= 1:
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
</t>
<t tx="nickcheng.20070126145908.5">def getproxylist(proxylisturl, testurls, proxies = {}, maxtime = 20, debug = True):
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
</t>
<t tx="nickcheng.20070126171343">abcccc
</t>
<t tx="nickcheng.20070126175658">@nosent roab.txt

Hello everyone~~~

&lt;&lt; Jul &gt;&gt;

Hello good bye
</t>
<t tx="nickcheng.20070126181144">sdfsdf
We add &lt;&lt; &gt;&gt; angle brackets to the headline. This tells Leo that the node is a section. 
We add the @c directive. This tells Leo where to start extracting text from this node. 
@c
sdfs
asdfasdfasd
keke
google
</t>
<t tx="nickcheng.20070126184322">assdd

</t>
</tnodes>
</leo_file>
