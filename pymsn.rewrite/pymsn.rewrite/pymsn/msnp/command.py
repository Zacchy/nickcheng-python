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

"""MSN protocol commands.

G{classtree Command}"""

from urllib import quote, unquote

__all__ = ['Command']

class Command(object):
    """Abstraction of MSN commands, this class enables parsing and construction
    of commands.
    
        @ivar name: the 3 uppercase letters name of the command
        @type name: string
        
        @ivar transaction_id: the transaction id of the command or None
        @type transaction_id: integer
        
        @ivar arguments: the arguments of the command
        @type arguments: tuple()
        
        @ivar payload: the payload of the command
        @type payload: string or None"""

    OUTGOING_NO_TRID = ('OUT', 'PNG')
    INCOMING_NO_TRID = (
            # NS commands
            'QNG', 'IPG', 'NOT', 'NLN', 'FLN', 'GCF',
            'QRY', 'SBS', 'UBN', 'UBM', 'UBX',
            # SW commands
            'RNG', 'JOI', 'BYE', 'MSG')

    OUTGOING_PAYLOAD = (
            'QRY', 'SDC', 'PGD', 'ADL', 'RML', 'UUN',
            'UUM', 'UUX', 'MSG')

    INCOMING_PAYLOAD = (
            'GCF', 'MSG', 'UBN', 'UBM', 'UBX', 'IPG',
            'NOT', 'ADL',
            
            '241')

    def __init__(self):
        self._reset()

    def _reset(self):
        """Resets the object values"""
        self.name = ''
        self.transaction_id = None
        self.arguments = None
        self.payload = None

    ### public methods
    def build(self, name, transaction_id, payload=None, *arguments):
        """Updates the command with the given parameters

            @param name: the command name (3 letters) (e.g. MSG NLN ...)
            @type name: string
            
            @param transaction_id: the transaction ID
            @type transaction_id: integer
            
            @param *arguments: the command arguments
            @type *arguments: string, ... 
            
            @param payload: is the data to send with the command
            @type payload: string
        """
        self.name = name
        self.transaction_id = transaction_id
        self.arguments = arguments
        self.payload = payload

    def parse(self, buf):
        """Fills the Command object according parsing a string.
            
            @param buf: the data to parse
            @type buf: string"""
        self._reset()
        lines = buf.split('\r\n', 1)
        self.__parse_command(lines[0])
        if len(lines) > 1: # payload
            self.payload = lines[1]
            # remove the last argument as it is the data length
            self.arguments = self.arguments[:-1]

    def is_error(self):
        """Tells if the current command is an error code
            
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
                result += ' ' + str(length) + '\r\n'
                if not self.is_error():
                    result += '\t[payload]'
                else:
                    result += self.payload

                return result
        return result

    def __parse_command(self, buf):
        words = buf.split()
        self.name, pos = words[0], 1
        if (words[0] not in self.INCOMING_NO_TRID) and\
                (words[0] not in self.OUTGOING_NO_TRID) and\
                len(words) > pos:
            self.transaction_id = int(words[pos])
            pos += 1
        if len(words) > pos:
            self.arguments = words[pos:]
