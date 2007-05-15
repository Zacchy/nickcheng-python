# -*- coding: utf-8 -*-
# pylint: disable-msg = W0613, W0611, R0914
#
# pymsn - a python client library for Msn
#
# Copyright (C) 2005-2006 Ali Sabil <ali.sabil@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""Utils
various utilities used by the library"""

__version__ = "$Id$"

import xml.sax
import xml.sax.handler
import xml.sax.saxutils
from httplib import HTTPException

from uuid import uuid1, uuid3, uuid4, uuid5
import consts

class Xml(xml.sax.handler.ContentHandler):
    "Very simplistic Xml parser"
    # --------------------------------------------------------------------------
    class Node:
        "Xml Node"
        def __init__( self, name, attrs ):
            self.name = name
            self.attributes = attrs
            self.cdata = ''
            self.childs = []

        def __getitem__(self, key):
            "Simplify attributes access"
            return self.get_attribute(key)

        def __getattr__(self, name):
            "Simplify childs access"
            return self.get_child(name)

        def add_child( self, child ):
            "Add a reference to a child element"
            self.childs.append(child)


        def get_child( self, name = None ):
            "Get a list of child elements"
            if name == None:
                return self.children

            result = []
            for child in self.childs:
                if child.name == name:
                    result.append(child)
            if len(result) == 1:
                return result[0]
            return result


        def get_attribute( self, key ):
            "Get an attribute value"
            return self.attributes.get(key)


        def get_content(self):
            "Get the cdata"
            return self.cdata
    # --------------------------------------------------------------------------
    def __init__(self):
        """Initializer"""
        xml.sax.handler.ContentHandler.__init__(self)
        self.root = None
        self.nodes_stack = []


    def startElement(self, name, attributes):
        "SAX start element even handler"
        node = self.Node( name.encode(), attributes )
        if len(self.nodes_stack) > 0:
            parent = self.nodes_stack[-1]
            parent.add_child(node)
        else:
            self.root = node
        self.nodes_stack.append(node)


    def endElement(self, name):
        "SAX end element event handler"
        self.nodes_stack = self.nodes_stack[:-1]


    def characters(self, data):
        "SAX character data event handler"
        if data.strip():
            data = data.encode('UTF-8')
            child = self.nodes_stack[-1]
            child.cdata += data
            return


    def parse(self, filename=None, text=None):
        "Parses a String or a file"
        if filename is not None:
            xml.sax.parse(filename, self)
        elif text is not None:
            xml.sax.parseString(text, self)

        return self.root

    def escape(self, text):
        return xml.sax.saxutils.escape(text)

def https_open( url, headers={}, data='', proxy=None, debug=1 ):
    """Open an https resource and return an httplib.HTTPResponse instance
        @param url: the url to open
        @param headers: headers to send to the server
        @param data: data to send to the server, just after the headers
        @param proxy: proxy to use for connection
        @type proxy L{gio.network.ProxyInfos}
        @param debug: debug level
        @type debug: integer"""
    from urlparse import urlsplit
    import httplib
    import socket
    import base64

    url_splitted = urlsplit(url, 'https')
    host = url_splitted[1].split(':')
    if len(host) == 1: # no port
        port = 443
        host = host[0]
    else:
        port = int(host[1])
        host = host[0]
    resource = url_splitted[2]

    if proxy is not None:
        client = httplib.HTTPConnection( host, port )
        client.set_debuglevel(debug)
        proxy_protocol  = 'CONNECT %s:%d HTTP/1.0\r\n' % ( host, port )
        if proxy.user:
            credentials = base64.encodestring( proxy.user+':'+proxy.password )
            proxy_protocol += 'Proxy-Authorization: Basic ' + credentials
        proxy_protocol += 'Host: %s\r\n' % host
        proxy_protocol += 'User-Agent: pymsn/0.2\r\n'
        proxy_protocol += '\r\n'
        if debug:
            print proxy_protocol

        proxy_client = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        proxy_client.connect( (proxy.host, proxy.port) )
        proxy_client.sendall( proxy_protocol )
        
        
        response = proxy_client.recv(8192)
        while '\r\n' not in response:
            response += proxy_client.recv(8192)
        status = response.split()[1]
        if status != "200":
            raise httplib.HTTPException(str(status))
        ssl = socket.ssl( proxy_client, None, None )
        sock = httplib.FakeSocket( proxy_client, ssl )
        client.sock = sock
    else:
        client = httplib.HTTPSConnection( host, port )
        client.set_debuglevel(debug)

    client.request('GET', resource, data, headers)
    return client.getresponse()

def compute_challenge(data):
    """
    Compute an answer for MSN Challenge from a given data

        @param data: the challenge string sent by the server
        @type data: string
    """
    import struct
    import md5
    def little_endify(value, c_type="L"):
        """Transform the given value into little endian"""
        return struct.unpack(">" + c_type, struct.pack("<" + c_type, value))[0]

    md5_digest = md5.md5(data + consts.PRODUCT_KEY).digest()
    # Make array of md5 string ints
    md5_integers = struct.unpack("<llll", md5_digest)
    md5_integers = [(x & 0x7fffffff) for x in md5_integers]
    # Make array of chl string ints
    data += consts.PRODUCT_ID
    amount = 8 - len(data) % 8
    data += "".zfill(amount)
    chl_integers = struct.unpack("<%di" % (len(data)/4), data)
    # Make the key
    high = 0
    low = 0
    i = 0
    while i < len(chl_integers) - 1:
        temp = chl_integers[i]
        temp = (consts.MAGIC_NUM * temp) % 0x7FFFFFFF
        temp += high
        temp = md5_integers[0] * temp + md5_integers[1]
        temp = temp % 0x7FFFFFFF
        high = chl_integers[i + 1]
        high = (high + temp) % 0x7FFFFFFF
        high = md5_integers[2] * high + md5_integers[3]
        high = high % 0x7FFFFFFF
        low = low + high + temp
        i += 2
    high = little_endify((high + md5_integers[1]) % 0x7FFFFFFF)
    low = little_endify((low + md5_integers[3]) % 0x7FFFFFFF)
    key = (high << 32L) + low
    key = little_endify(key, "Q")
    longs = [x for x in struct.unpack(">QQ", md5_digest)]
    longs = [little_endify(x, "Q") for x in longs]
    longs = [x ^ key for x in longs]
    longs = [little_endify(abs(x), "Q") for x in longs]
    out = ""
    for value in longs:
        value = hex(value)
        value = value[2:-1]
        value = value.zfill(16)
        out += value.lower()
    return out
