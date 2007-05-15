# -*- coding: utf-8 -*-
#
# pymsn - a python client library for Msn
#
# Copyright (C) 2005-2006 Ali Sabil <ali.sabil@gmail.com>
# Copyright (C) 2006  Johann Prieur <johann.prieur@gmail.com>
# Copyright (C) 2006  Ole André Vadla Ravnås <oleavr@gmail.com>
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

"""Transport
Protocol transport module.

This module contains classes used by the library to connect to the msn server
it includes for example, the direct connection transport as well as an http
polling transport ideal in firewalled environment."""

__version__ = "$Id$"

import logging
import gobject

import gio
import structure

from consts import ServerType

logger = logging.getLogger('Connection')

class BaseTransport(gobject.GObject):
    """Abstract Base Class that modelize a connection to an MSN service"""
    
    __gsignals__ = {
            "connection-failure" : (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                ()),

            "connection-success" : (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                ()),

            "connection-reset" : (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                ()),

            "connection-lost" : (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                ()),

            "command-received": (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                (object,)),

            "command-sent": (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                (object,)),
            }   

    def __init__(self, server):
        """Connection initialization
        
            @param server: the server to connect to.
            @type server: (host: string, port: integer)"""
        gobject.GObject.__init__(self)
        self.server = server
        self._transaction_id = 0
    
    def __get_transaction_id(self):
        return self._transaction_id
    transaction_id = property(__get_transaction_id,
            doc="return the current transaction id")

    # Connection
    def establish_connection(self):
        """Connect to the server server"""
        raise NotImplementedError

    def lose_connection(self):
        """Disconnect from the server"""
        raise NotImplementedError

    def reset_connection(self, server=None):
        """Reset the connection

            @param server: when set, reset the connection and
                connect to this new server
            @type server: (host: string, port: integer)"""
        raise NotImplementedError

    # Command Sending
    def send_command(self, command, increment=True, callback=None, cb_args=()):
        """
        Sends a L{structure.Command} to the server.

            @param command: command to send
            @type command: L{structure.Command}

            @param increment: if False, the transaction ID is not incremented
            @type increment: bool

            @param callback: callback to be used when the command has been
                transmitted
            @type callback: callable

            @param cb_args: callback arguments
            @type cb_args: tuple
        """
        raise NotImplementedError

    def send_command_ex(self, command, arguments=None, payload=None,
            transaction_id=-1, increment=True, callback=None, cb_args=()):
        """
        Builds a command object then send it to the server.
        
            @param command: the command name, must be a 3 letters
                uppercase string.
            @type command: string
        
            @param arguments: command arguments
            @type arguments: (string, ...)
        
            @param payload: payload data
            @type payload: string

            @param increment: if False, the transaction ID is not incremented
            @type increment: bool

            @param callback: callback to be used when the command has been
                transmitted
            @type callback: callable

            @param cb_args: callback arguments
            @type cb_args: tuple
        """
        raise NotImplementedError

    def _increment_transaction_id(self):
        """Increments the Transaction ID then return it.
            
            @rtype: integer"""
        self._transaction_id += 1
        return self._transaction_id

gobject.type_register(BaseTransport)


class DirectConnection(BaseTransport):
    """Implements a direct connection to the net without any proxy""" 

    def __init__(self, server):
        BaseTransport.__init__(self, server)
        
        transport = gio.network.TCPClient(server[0], server[1])
        transport.connect("notify::status", self.__on_status_change)
        transport.connect("error", lambda t, msg: self.emit("connection-failure"))

        receiver = gio.ChunkReceiver(transport)
        receiver.connect("received", self.__on_received)

        self._receiver = receiver
        self._receiver.delimiter = "\r\n"
        self._transport = transport
        self.__pending_chunk = None
        self.__resetting = False
        
    __init__.__doc__ = BaseTransport.__init__.__doc__

    ### public commands
    
    def establish_connection(self):
        logger.debug('<-> Connecting to %s:%d' % self.server )
        self._transport.open()

    def lose_connection(self):
        self._transport.close()

    def reset_connection(self, server=None):
        if server:
            self._transport.set_property("host", server[0])
            self._transport.set_property("port", server[1])
            self.server = server
        self.__resetting = True
        self._transport.close()
        self._transport.open()

    def send_command(self, command, increment=True, callback=None, cb_args=()):
        logger.debug('>>> ' + repr(command))
        our_cb_args = (command, callback, cb_args)
        self._transport.send(str(command), self.__on_command_sent, our_cb_args)
        if increment:
            self._increment_transaction_id()

    def __on_command_sent(self, command, user_callback, user_cb_args):
        self.emit("command-sent", command)

        if user_callback:
            user_callback(*user_cb_args)

    def send_command_ex(self, command, arguments=None, payload=None,
            transaction_id=-1, increment=True, callback=None, cb_args=()):
        if transaction_id is not None and transaction_id < 0:
            transaction_id = self._transaction_id
        cmd = structure.Command()
        cmd.build(command, transaction_id, arguments, payload)
        self.send_command(cmd, increment, callback, cb_args)

    ### callbacks
    def __on_status_change(self, transport, param):
        status = transport.get_property("status")
        if status == gio.STATUS_OPEN:
            if self.__resetting:
                self.emit("connection-reset")
                self.__resetting = False
            self.emit("connection-success")
        elif status == gio.STATUS_CLOSED:
            if not self.__resetting:
                self.emit("connection-lost")

    def __on_received(self, receiver, chunk):
        cmd = structure.Command()
        if self.__pending_chunk:
            chunk = self.__pending_chunk + "\r\n" + chunk
            cmd.parse(chunk)
            self.__pending_chunk = None
            self._receiver.delimiter = "\r\n"
        else:
            cmd.parse(chunk)
            if cmd.name in structure.Command.PAYLOAD_COMMANDS:
                payload_len = int(cmd.arguments[-1])
                if payload_len > 0:
                    self.__pending_chunk = chunk
                    self._receiver.delimiter = payload_len
                    return
                
        logger.debug('<<< ' + repr(cmd))
        self.emit("command-received", cmd)

gobject.type_register(DirectConnection)
 
class HTTPPollConnection(BaseTransport):
    """Implements an http connection to the net without any proxy"""
    
    def __init__(self, server, server_type=ServerType.NOTIFICATION):
        BaseTransport.__init__(self, server)

        transport = gio.network.TCPClient(server[0], server[1])
        self.status_id = transport.connect("notify::status", self.__on_status_change)
        transport.connect("error", lambda t, msg: self.emit("connection-failure"))
        # self._die = False

        logger.debug(self.status_id)

        receiver = gio.ChunkReceiver(transport)
        receiver.connect("received", self.__on_received)
        
        self._receiver = receiver
        self._receiver.delimiter = "\r\n"
        self._transport = transport
        self.__resetting = False

        self.command_queue = []
        self.waiting_for_response = False
        self.notification = True
        self.server_type = server_type

        # Configuring the polling period
        gobject.timeout_add(3000, self.__poll)
        
        self.__clear_response_handler()
    __init__.__doc__ = BaseTransport.__init__.__doc__ + \
            """

            @param server_type: the server type
            @type server_type: L{consts.ServerType}"""

    # Connection
    def establish_connection(self):
        logger.debug('<-> Connecting to %s:%d' % self.server )
        self._transport.open()

    def lose_connection(self):
        self._transport.close()

    def reset_connection(self, server=None):
        if server:
            self._transport.set_property("host", server[0])
            self._transport.set_property("port", server[1])
            self.server = server
        self.__resetting = True
        self._transport.close()
        self._transport.open()

    # Command Sending
    def send_command(self, command=None, increment=True, callback=None,
            cb_args=()):
        if len(self.command_queue) > 0 or self.waiting_for_response:
            self.command_queue.insert(0, (command, increment, callback, cb_args))
        else:        
            self.__send_it(command, increment, callback, cb_args)

    def __send_it(self, command, increment=True, user_callback=None,
            user_cb_args=()):
        host = self._transport.get_property("host")
        strcmd = str(command)
        lstrcmd = len(strcmd)

        if self.notification:            
            params = "Action=open&Server=%s&IP=%s" % (self.server_type, host)
            self.notification = False
        elif command == None:
            # Polling the server for queued messages
            params = "Action=poll&SessionID=%s" % self.session_id
            strcmd = ""
            lstrcmd = 0
        else:
            params = "SessionID=%s" % self.session_id

        header = ("POST http://%s/gateway/gateway.dll?%s HTTP/1.1\r\n" +\
                 "Accept: */*\r\n" +\
                 "Accept-Language: en-us\r\n" +\
                 "User-Agent: MSMSGS\r\n" +\
                 "Host: %s\r\n" +\
                 "Proxy-Connection: Keep-Alive\r\n" +\
                 "Connection: Keep-Alive\r\n" +\
                 "Pragma: no-cache\r\n" +\
                 "Content-Type: application/x-msn-messenger\r\n" +\
                 "Content-Length: %d\r\n") % (host, params, host, lstrcmd)

        self._transport.send(header + "\r\n" + strcmd)
        self.waiting_for_response = True

        logger.debug('>>> ' + repr(command))
        
        if increment:
            self._increment_transaction_id()
        
        if user_callback:
            user_callback(*user_cb_args)

    def send_command_ex(self, command, arguments=None, payload=None,
            transaction_id=-1, increment=True, callback=None, cb_args=()):
        if transaction_id is not None and transaction_id < 0:
            transaction_id = self._transaction_id
        cmd = structure.Command()
        cmd.build(command, transaction_id, arguments, payload)
        self.send_command(cmd, increment, callback, cb_args)

    ### callbacks
    def __on_status_change(self, transport, param):
        status = transport.get_property("status")
        if status == gio.STATUS_OPEN:
            if self.__resetting:
                self.emit("connection-reset")
                self.__resetting = False
            self.emit("connection-success")
        elif status == gio.STATUS_CLOSED:
            if not self.__resetting:
                self.emit("connection-lost")

    def __poll(self):
        self.send_command()
        return True

    def __on_received(self, receiver, chunk):
        if chunk[:4] == 'HTTP':
            # If required test connection status here. See :
            # http://www.w3.org/Protocols/rfc2616/rfc2616-sec8.html
            # http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.1.1
            pass
        elif self.waiting_for_data:
            self.data = chunk
        elif len(chunk) == 0:
            self._receiver.delimiter = self.content_length
            self.waiting_for_data = True
        else:
            header, content =  [p.strip() for p in chunk.split(':', 1)]
            if header == 'Content-Length':
                self.content_length = int(content)
            elif header == 'X-MSN-Messenger':
                for elem in content.split(';'):
                    key, value =  [p.strip() for p in elem.split('=', 1)]
                    if key == 'SessionID':
                        self.session_id = value
                    elif key == 'GW-IP':
                        self._transport.set_property("host", value)
                    elif key == 'Session'and value == 'close':
                        # Connection is lost before receiving the close message
                        # TODO : check why in gio and then debug
                        # self._die = True
                        self.lose_connection()

        if self.waiting_for_data:
            if self.content_length == 0:
                logger.debug('>>> Poll : no message queued on server')
            elif len(self.data) != 0:
                while len(self.data) != 0:
                    self.data = self.__extract_command(self.data)
            self.waiting_for_response = False
            self.__clear_response_handler()
            self._receiver.delimiter = '\r\n'
            if len(self.command_queue) > 0:
                (cmd, inc, callback, cb_args) = self.command_queue.pop()
                self.__send_it(cmd, inc)

    def __extract_command(self, data):
        first, rest = data.split('\r\n', 1)
        cmd = structure.Command()
        cmd.parse(first.strip())
        if cmd.name in structure.Command.PAYLOAD_COMMANDS:
            payload_len = int(cmd.arguments[-1])
            if payload_len > 0:
                cmd.payload = rest[:payload_len].strip()
            logger.debug('<<< ' + repr(cmd))
            self.emit("command-received", cmd)
            return rest[payload_len:]
        else:
            logger.debug('<<< ' + repr(cmd))
            self.emit("command-received", cmd)
            return rest

    def __clear_response_handler(self):
        self.waiting_for_data = False
        self.data = ''
        self.content_length = 0
            
gobject.type_register(HTTPPollConnection)
