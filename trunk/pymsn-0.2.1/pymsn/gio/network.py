# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2006  Ole André Vadla Ravnås <oleavr@gmail.com>
# Copyright (C) 2006  Ali Sabil <ali.sabil@gmail.com>
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
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

"""Network I/O.

This module provides asynchronous network I/O.

@group Client: AbstractClient, SocketClient, TCPClient
@group Proxy: ProxyInfos, HttpConnectClient"""

import gobject
import socket
import logging
import base64

from socket import AF_UNIX, AF_INET, AF_INET6, SOCK_STREAM,\
    SOCK_DGRAM, SOCK_RAW, SOCK_RDM, SOCK_SEQPACKET

from constants import *
from receiver import ChunkReceiver

logger = logging.getLogger('gio.transport')

class ProxyInfos(object):
    """Contain informations needed to make use of a proxy.

        @ivar host: hostname of the proxy server.
        @ivar port: port used to connect to server.
        @ivar type: proxy type
        @ivar user: username to use for authentication.
        @ivar password: password to use for authentication.
        @undocumented __*_port, __str__

        @since: 0.1"""
    
    def __init__(self, host, port, type='http', user=None, password=None):
        """Initializer
            
            @param host: the hostname of the proxy server.
            @type host: string
            
            @param port: the port used to connect to server.
            @type port: integer > 0 and < 65536

            @param type: proxy type
            @type type: string in ('http', 'https', 'socks4', 'socks5')

            @param user: the username to use for authentication.
            @type user: string
            
            @param password: the password to use for authentication.
            @type password: string"""

        self.host = host
        self._port = int(port)
        self.type = type
        self.user = user
        self.password = password
    
    def __get_port(self):
        return self._port
    def __set_port(self, port):
        self._port = int(port)
        assert(self._port >= 0 and self._port <= 65535)
    port = property(__get_port, __set_port, doc="port used to connect to server.")

    def __str__(self):
        host = '%s:%u' % (self.host, self._port)
        if self.user:
            auth = '%s:%s' % (self.user, self.password)
            host = auth + '@' + host
        return self.type + '://' + host + '/'

class AbstractClient(gobject.GObject):
    """Abstract client base class.
    All network client classes implements this interface.
        
        @sort: __init__, open, send, close
        @undocumented: do_*, _change_status
        
        @since: 0.1"""
    
    __gproperties__ = {
            "host": (gobject.TYPE_STRING,
                "Remote Host",
                "The remote host to connect to.",
                "",
                gobject.PARAM_READWRITE),

            "port": (gobject.TYPE_INT,
                "Remote Port",
                "The remote port to connect to.",
                -1, 65535, -1,
                gobject.PARAM_READWRITE),
            
            "proxy": (object,
                "Connection proxy",
                "a ProxyInfos instance.",
                gobject.PARAM_READWRITE),
            
            "status": (gobject.TYPE_INT,
                "Connection Status",
                "The status of this connection.",
                0, 3, STATUS_CLOSED,
                gobject.PARAM_READABLE),
            }
        
    __gsignals__ = {
            "error": (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                (gobject.TYPE_STRING,)),

            "received": (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                (object, gobject.TYPE_ULONG)),

            "sent": (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                (object, gobject.TYPE_ULONG)),
            }
    
    def __init__(self, host, port, proxy=None):
        """Initializer

            @param host: the hostname to connect to.
            @type host: string
            
            @param port: a port number to connect to
            @type port: integer > 0 and < 65536

            @param proxy: proxy infos
            @type proxy: L{ProxyInfos}
        """
        gobject.GObject.__init__(self)
        
        self._host = host
        self._port = port
        self._proxy = proxy

        self._status = STATUS_CLOSED

    def _change_status(self, new_status):
        self._status = new_status
        self.notify("status")

    def do_get_property(self, pspec):
        if pspec.name == "host":
            return self._host
        elif pspec.name == "port":
            return self._port
        elif pspec.name == "proxy":
            return self._proxy
        elif pspec.name == "status":
            return self._status
        else:
            raise AttributeError, "unknown property %s" % pspec.name

    def do_set_property(self, pspec, value):
        if pspec.name == "host":
            self._host = value
        elif pspec.name == "port":
            self._port = value
        elif pspec.name == "proxy": # TODO: Check type ?
            self._proxy = value
        else:
            raise AttributeError, "unknown property %s" % pspec.name

    def open(self):
        """Open the connection."""
        raise NotImplemented

    def close(self):
        """Close the connection."""
        raise NotImplemented

    def send(self, buf, callback=None, cb_args=()):
        """Send data to the server.
        
            @param buf: data buffer.
            @type buf: string
            
            @param callback: a callback method that would be called when the
                data is atually sent to the server.
            @type callback: callback
            
            @param cb_args: callback arguments to be passed to the callback.
            @type cb_args: tuple"""
        raise NotImplemented
gobject.type_register(AbstractClient)


class SocketClient(AbstractClient):
    """Asynchronous Socket client class.
        
        @note: doesn't support proxy
        @sort: __init__, open, send, close
        @undocumented: do_*, __reset_state, _watch_*, _io_*, _connect_done_handler

        @since: 0.1"""
    
    def __init__(self, host="", port=-1, domain=AF_INET, type=SOCK_STREAM):
        """Initializer

            @param host: the hostname to connect to.
            @type host: string
            
            @param port: the port number to connect to.
            @type port: integer > 0 and < 65536
            
            @param domain: the communication domain.
            @type domain: integer
            @see L{socket} module

            @param type: the communication semantics
            @type type: integer
            @see L{socket} module"""

        AbstractClient.__init__(self, host, port)
        
        self._domain = domain
        self._type = type

        self.__reset_state()
        
        self._status = STATUS_CLOSED
    
    def __reset_state(self):
        s = socket.socket(self._domain, self._type)
        s.setblocking(0)

        ch = gobject.IOChannel(s.fileno())
        ch.set_flags(ch.get_flags() | gobject.IO_FLAG_NONBLOCK)
        ch.set_encoding(None)
        ch.set_buffered(False)
        
        self._socket = s
        self._chan = ch

        self._source_id = None
        self._source_cond = 0
        self._queue = []
    
    def open(self):
        
        if len(self._host) == 0 or self._port == -1:
            raise ValueError("Wrong host or port number : (%s, %d)" % (self._host, self._port) )
        
        if self._status in (STATUS_OPENING, STATUS_OPEN):
            return

        assert(self._status == STATUS_CLOSED)
        
        self._change_status(STATUS_OPENING)

        try:
            self._socket.connect((self._host, self._port))
        except socket.error, e:
            pass
        
        self._watch_change(gobject.IO_PRI | gobject.IO_IN |
                           gobject.IO_OUT | gobject.IO_HUP |
                           gobject.IO_ERR | gobject.IO_NVAL,
                           self._connect_done_handler)
    open.__doc__ = AbstractClient.open.__doc__

    
    def close(self):
        if self._status in (STATUS_CLOSING, STATUS_CLOSED):
            return
        
        self._change_status(STATUS_CLOSING)
        
        self._watch_remove()
        self._chan.close()
        try:
            self._socket.shutdown(socket.SHUT_RDWR)
        except:
            pass
        self._socket.close()
        
        self.__reset_state()
        self._change_status(STATUS_CLOSED)
    close.__doc__ = AbstractClient.close.__doc__
    
    def send(self, buf, callback=None, cb_args=()):
        assert(self._status == STATUS_OPEN)
        
        self._queue.append([ buf, False, callback, cb_args ])
        self._watch_add_cond(gobject.IO_OUT)
    send.__doc__ = AbstractClient.send.__doc__

    ### convenience methods

    def _watch_remove(self):
        if self._source_id is not None:
            gobject.source_remove(self._source_id)
            self._source_id = None
            self._source_cond = 0

    def _watch_change(self, cond, handler=None):
        self._watch_remove()
        self._source_cond = cond
        if handler is None:
            handler = self._io_channel_handler
        self._source_id = self._chan.add_watch(cond, handler)
    
    def _watch_add_cond(self, cond):
        if self._source_cond & cond:
            return
        
        self._source_cond |= cond
        self._watch_change(self._source_cond)

    def _watch_remove_cond(self, cond):
        if not self._source_cond & cond:
            print "_watch_remove_cond: cond not set"
            return
        
        self._source_cond ^= cond
        self._watch_change(self._source_cond)


    ### asynchronous callbacks

    def _connect_done_handler(self, chan, cond):
        self._watch_remove()
        
        opts = self._socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        if opts == 0:
            self._watch_change(gobject.IO_IN | gobject.IO_PRI |
                               gobject.IO_ERR | gobject.IO_HUP)
            self._change_status(STATUS_OPEN)
            
        else:
            self._change_status(STATUS_CLOSED)
            self.emit("error", "connection failed")
        
        return False
    
    def _io_channel_handler(self, chan, cond):
        if self._status == STATUS_CLOSED:
            return False
        
        # Check for error/EOF
        if cond & (gobject.IO_ERR | gobject.IO_HUP):
            self.close()
            return False
        
        # Incoming
        if cond & (gobject.IO_IN | gobject.IO_PRI):
            buf = self._chan.read()
            if buf == "":
                self.close()
                return False
            self.emit("received", buf, len(buf))

        # Outgoing
        if cond & gobject.IO_OUT:            
            # Grab an item
            item = self._queue[0]
            if item[1]: # is it sent?
                self.emit("sent", item[0], len(item[0]))
                del self._queue[0]
                
                # Callback provided?
                if item[2]:
                    item[2](*item[3])
            
            # Any more remaining?
            if len(self._queue) > 0:
                item = self._queue[0]
                self._chan.write(item[0])
                item[1] = True
            else:
                self._watch_remove_cond(gobject.IO_OUT)

        return True

gobject.type_register(SocketClient)

class TCPClient( SocketClient ):
    """Asynchronous TCP client class.
        
        @sort: __init__, open, send, close
        @undocumented: do_*, __reset_state, _watch_*, _io_*, _connect_done_handler

        @since: 0.1"""

    def __init__(self, host="", port=-1):
        """TCPClient initializer

            @param host: the hostname to connect to.
            @type host: string
            
            @param port: the port number to connect to.
            @type port: integer > 0 and < 65536"""

        SocketClient.__init__(self, host, port, AF_INET, SOCK_STREAM)

gobject.type_register(TCPClient)


class HttpConnectClient(AbstractClient):
    """HttpConnectClient class.
        
        @undocumented: do_*, __reset_state, __on_*

        @since: 0.1"""

    PROXY_TYPES = ('http', 'https')
    
    def __init__(self, host, port, proxy):
        assert(proxy.type in PROXY_TYPES)
        ProxyfiedClient.__init__(self, host, port, proxy)
        self._transport = TCPClient(proxy.host, proxy.port)
        self._transport.connect("notify::status", self.__on_status_change)
        self._transport.connect("sent", self.__on_sent)
        self._transport.connect("error", lambda t, msg: self.emit("error", "proxy connection refused"))

        self._receiver = gio.ChunkReceiver(self._transport)
        self._receiver.connect("received", self.__on_received)
        self.__reset_state()
    __init__.__doc__ = AbstractClient.__init__.__doc__
        
    def __reset_state(self):
        self._receiver.delimiter = '\r\n\r\n'
        self._status = STATUS_CLOSED

    def open(self):
        self._transport.open()
    open.__doc__ = AbstractClient.open.__doc__

    def close(self):
        self._transport.close()
    close.__doc__ = AbstractClient.close.__doc__

    def send(self, buf, callback=None, cb_args=()):
        assert(self._status == STATUS_OPEN)
        self._transport.send(buf, callback, cb_args)
    send.__doc__ = AbstractClient.send.__doc__

    def __on_status_change(self,  transport, param):
        status = transport.get_property("status")
        if status == STATUS_OPEN:
            proxy_protocol  = 'CONNECT %s:%s HTTP/1.0\r\n' % (self._host, self._port)
            proxy_protocol += 'Proxy-Connection: Keep-Alive\r\n'
            proxy_protocol += 'Pragma: no-cache\r\n'
            proxy_protocol += 'Host: %s:%s\r\n' % (self._host, self._port),
            proxy_protocol += 'User-Agent: gio/0.2\r\n'
            if self._proxy.user:
                auth = base64.encodestring(self._proxy.user + ':' + self._proxy.password)
                proxy_protocol += 'Proxy-authorization: Basic ' + auth + '\r\n'
            proxy_protocol += '\r\n'            
            self._transport.send(proxy_protocol)
        else:
            self._change_status(status)
            
    def __on_sent(self, transport, data, length):
        if self.get_property("status") == STATUS_OPEN:
            self.emit("sent", data, length)
    
    def __on_received(self, receiver, chunk):
        if self.get_property("status") == STATUS_OPENING:
            if chunk.split(' ')[1] != "200":
                self.emit("error", chunk.split('\r\n',1)[0])
            else:
                self._receiver.delimiter = None
                self._change_status(STATUS_OPEN)
        else:
            self.emit("received", chunk)

gobject.type_register(HttpConnectClient)

