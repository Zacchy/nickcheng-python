# -*- coding: utf-8 -*-
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

"""Structure
Contain various structures used to abstract the MSN protocol
commands and messages.

The L{Command} class abstract all MSN commands, where the L{Message}
class abstract the content of the MSG command, which is a special command
in the MSN protocol."""

__version__ = "$Id$"

from urllib import quote, unquote

class Command(object):
    """
    Abstraction of MSN commands, this class enables parsing and construction
    of commands
    """

    NO_TRANSACTION_ID_COMMANDS = (  # NS commands
                                    'PNG', 'QNG', 'NLN', 'FLN', 'BPR', 'MSG',
                                    'IPG', 'NOT', 'GTC', 'BLP', 'PRP', 'LSG',
                                    'LST', 'OUT', 'UBX',
                                    # SW commands
                                    'RNG', 'JOI', 'BYE', 'MSG'
                                    )
    # QRY is a actually a payload command, but only when we send it
    # same goes for SDC, PGD
    PAYLOAD_COMMANDS = ('MSG', 'IPG', 'NOT', 'GCF', 'UBX')

    def __init__(self):
        self.name = ''
        self.transaction_id = None
        self.arguments = None
        self.payload = None
        
    ### internal convenience
    def __init_state(self):
        """Resets the object values"""
        self.name = ''
        self.transaction_id = None
        self.arguments = None
        self.payload = None

    ### public methods
    def build(self, name, transaction_id, arguments=None, payload=None):
        """Updates the command with the given parameters

            @param name: the command name (3 letters) (e.g. MSG NLN ...)
            @type name: string
            
            @param transaction_id: the transaction ID
            @type transaction_id: integer
            
            @param arguments: the command arguments as a sequence
            @type arguments: (arg1: string, ...) 
            
            @param payload: is the data to send with the command
            @type payload
        """
        self.name = name
        self.transaction_id = transaction_id
        self.arguments = arguments
        self.payload = payload

    def parse(self, buf):
        """Fills the Command object according parsing a string.
            
            @param buf: the data to parse
            @type buf: string"""
        self.__init_state()
        lines = buf.split('\r\n', 1)
        if len(lines) == 1:
            self.__parse_command(buf) # normal command
        else: #payload
            self.payload = lines[1]
            self.__parse_command(lines[0])
            # remove the last argument as it is the data length
            self.arguments = self.arguments[:-1]

        if self.arguments is not None and len(self.arguments) == 0:
            self.arguments = None

    def is_error(self):
        """Tells if the current comment is an error code
            
            @rtype: bool"""
        try:
            int(self.name)
        except ValueError:
            return False
        else:
            return True

    def is_payload(self):
        """Tells if the current comment is a payload command
        
            @rtype: bool"""
        return self.payload is not None

    ### private and special methods
    def __str__(self):
        result = self.name[:]
        if self.transaction_id is not None:
            result += ' ' + str(self.transaction_id)

        if self.arguments is not None and len(self.arguments) > 0:
            result += ' ' + ' '.join(self.arguments)

        if self.payload is not None:
            length = len(self.payload)
            if length > 0:
                result += ' ' + str(length) + '\r\n' + self.payload
                return result

        return result + '\r\n'

    def __repr__(self):
        result = self.name[:]
        if self.transaction_id is not None:
            result += ' ' + str(self.transaction_id)

        if self.arguments is not None and len(self.arguments) > 0:
            result += ' ' + ' '.join(self.arguments)

        if self.payload is not None:
            length = len(self.payload)
            if length > 0:
                result += ' ' + str(length) + '\r\n' + '[payload]'
                return result
        return result

    def __parse_command(self, buf):
        words = buf.split()
        self.name, pos = words[0], 1
        if words[0] not in self.NO_TRANSACTION_ID_COMMANDS:
            if len(words) > pos:
                self.transaction_id = int(words[pos])
                pos += 1
        if len(words) > pos:
            self.arguments = words[pos:]

class Message(object):
    """Base Messages class.
    
        @ivar passport: sender passport
        @type passport: string
        
        @ivar friendly_name: sender friendly name
        @type friendly_name: string
        
        @ivar body: message body
        @type body: string
        
        @ivar headers: message headers
        @type headers: {header_name: string => header_value:string}"""

    def __init__(self, body=""):
        """Initializer
            
            @param body: The body of the message, it is put after the headers
            @type body: string"""
        self.passport = 'Hotmail'
        self.friendly_name = 'Hotmail'
        self.body = body
        self.headers = {'MIME-Version' : '1.0', 'Content-Type' : 'text/plain'}

    def __str__(self):
        """Represents the payload of the message
        
        the representation looks like this ::
            header1: header-content\\r\\n
            ...\\r\\n
            \\r\\n
            body
            
        @rtype: string"""
        message = ''
        for header in self.headers:
            message += header + ': '+ self.headers[header] + '\r\n'
        message += '\r\n' + self.body
        return message

    def __repr__(self):
        """Represents the payload of the message"""
        message = ''
        if 'Content-Type' in self.headers:
            message += 'Content-Type: ' + self.headers['Content-Type']
        else:
            message += 'Content-Type: text/plain'
        message += '\r\n' + 'Headers-count: ' + str(len(self.headers))
        message += '\r\n' + '[message body]'
        return message

    def __get_content_type(self):
        if 'Content-Type' in self.headers:
            content_type = self.headers['Content-Type'].split(';', 1)
            if len(content_type) == 1:
                return (content_type[0].strip(), 'UTF-8')
            mime_type = content_type[0].strip()
            encoding = content_type[1].split('=', 1)[1].strip()
            return (mime_type, encoding)
        return ('text/plain', 'UTF-8')
    
    def __set_content_type(self, content_type):
        if len(content_type) == 1:
            content_type = (content_type, 'UTF-8')
        content_type = '; charset='.join(content_type)
        self.headers['Content-Type'] = content_type

    content_type = property(__get_content_type, __set_content_type,
            doc="a tuple specifying the content type")

    def _parse_header(self, headers):
        """Parse a string extracting HTTP style headers and filling the
        self.headers attribute"""
        headers = headers.split('\r\n')
        for header in headers:
            key, value = header.split(':', 1)
            self.headers[key.strip()] = value.strip()

class IncomingMessage(Message):
    """Incoming Message abstraction"""

    def __init__(self, command):
        """Initializer
        
            @param command: the MSG command received from the server
            @type command: L{structure.Command}"""
        Message.__init__(self)

        self.passport = command.arguments[0]
        self.friendly_name = unquote(command.arguments[1])
        message = command.payload.split('\r\n\r\n', 1)
        self._parse_header(message[0])
        if len(message) == 1:
            self.body = ''
        else:
            self.body = message[1]

    def __str__(self):
        """Represents the message
        
        the representation looks like this ::
            MSG sender-passport sender-friendly-name payload-size\\r\\n
            header1: header-content\\r\\n
            ...\\r\\n
            \\r\\n
            body
            
        @rtype: string"""
        message = Message.__str__(self)
        command = 'MSG %s %s %u\r\n' % (   self.passport,
                                            quote(self.friendly_name),
                                            len(message))
        return command + message
    
    def __repr__(self):
        """Represents the message"""
        message = Message.__repr__(self)
        command = 'MSG %s %s %u\r\n' % (   self.passport,
                                            quote(self.friendly_name),
                                            len(message))
        return command + message



class OutgoingMessage(Message):
    """Build MSG commands destined to be sent."""

    def __init__(self, transaction_id, ack):
        """Initializer
        
            @param transaction_id: the transaction ID
            @type transaction_id: integer
            
            @param ack: Acknowledgment type
            @type ack: L{consts.MessageAcknowledgement}"""
        Message.__init__(self)
        self.transaction_id = transaction_id
        self.ack = ack
        self.passport = ''
        self.friendly_name = ''

    def __str__(self):
        """Represents the message
        
        the representation looks like this ::
            MSG transaction-id ack payload-size\\r\\n
            header1: header-content\\r\\n
            ...\\r\\n
            \\r\\n
            body
            
        @rtype: string"""
        message = Message.__str__(self)
        command = 'MSG %u %s %u\r\n' % \
                (self.transaction_id, self.ack, len(message) )
        return command + message

    def __repr__(self):
        """Represents the message"""
        message = Message.__repr__(self)
        command = 'MSG %u %s %u\r\n' % \
                (self.transaction_id, self.ack, len(message) )
        return command + message

