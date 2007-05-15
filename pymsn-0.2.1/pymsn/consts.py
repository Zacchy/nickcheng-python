# -*- coding: utf-8 -*-
#
# pymsn - a python client library for Msn
#
# Copyright (C) 2005-2006 Ali Sabil <ali.sabil@gmail.com>
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

"""Consts
Various contants used by the library."""

__version__ = "$Id$"

VER = ('MSNP11','CVR0')
CVR = ('0x0409', 'winnt', '5.1', 'i386', 'MSNMSGR', '7.0.0813', 'MSMSGS')
ID = 1073774596 # capabilities
PRODUCT_ID = "PROD0090YUAUV{2B"
PRODUCT_KEY = "YMM8C_H7KCQ2S_KL"
MAGIC_NUM = 0x0E79A9C1
PASSPORT_NEXUS = "https://nexus.passport.com:443/rdr/pprdr.asp"

# TODO: use standard constants here if possible
UINT32_MIN = 0
UINT32_MAX = 4294967295
UINT64_MIN = 0
UINT64_MAX = 18446744073709551615

class ContactListStatus(object):
    """Contact list synchronization status.
    
    A contact list is said to be synchronized when it
    matches the contact list stored on the server."""
    
    NOT_SYNCHRONIZED = 0
    """The contact list is not synchronized yet"""
    SYNCHRONIZING = 1
    """The contact list is being synchronized"""
    SYNCHRONIZED = 2
    """The contact list is already synchornized"""

class SwitchboardStatus(object):
    """Switchboard connection status"""
    
    CONNECTED = 1
    """Connected to the switchboard"""
    AUTHENTICATING = 2
    """Connected to the switchboard, but still authenticating"""
    AUTHENTICATED = 3
    """The authentication succeded, and the switchboard is about to be open"""
    OPENING = 4
    """The switchboard is opening, waiting for contacts to join in"""
    OPENED = 5
    """The switchboard is open, and it is possible to send messages"""
    CLOSED = 6
    """Disconnected from the switchboard"""
    IDLE = 7
    """Disconnected from the switchboard because of idle status"""
    
class PresenceStatus(object):
    """Presence states"""
    ONLINE = 'NLN'
    """Online"""
    BUSY = 'BSY'
    """Busy, do not disturb"""
    IDLE = 'IDL'
    """No activity"""
    AWAY = 'AWY'
    """Away from keyboard"""
    BE_RIGHT_BACK = 'BRB'
    """Back in a few minutes"""
    ON_THE_PHONE = 'PHN'
    """Currently on phone"""
    OUT_TO_LUNCH = 'LUN'
    """Having lunch"""
    INVISIBLE = 'HDN'
    """Hidden from other contacts"""
    OFFLINE = 'FLN'
    """Offline"""

class MessageAcknowledgement(object):
    """Message Acknowledgement"""
    FULL = 'A'
    """Acknowledgement required for both delivery success and failure"""
    MSNC = 'D'
    """Direct connection, no acknowledgment required from the server"""
    HALF = 'N'
    """Acknowledgment on delivery failures"""
    NONE = 'U'
    """No Acknowledgment"""
 
class ServerType(object):
    SWITCHBOARD = 'SB'
    NOTIFICATION = 'NS'

class List(object):
    """Lists are sets, that contain contacts, do
    define their current status in the contact list.
    """
    
    FORWARD = 'FL'
    """Contact is visible in the contact list"""
    REVERSE = 'RL'
    """We are visible in the contact's contact list"""
    ALLOW = 'AL'
    """Contact is allowed to see our L{PresenceStatus}"""
    BLOCK = 'BL'
    """Contact is not allowed to see our L{PresenceStatus}"""
    PENDING = 'PL'
    """Contact is waiting to be added to our contact list"""

    code = {FORWARD:1, ALLOW:2, BLOCK:4, REVERSE:8, PENDING:16}

class DefaultPrivacy(object):
    """Privacy modes""" 
    ALLOW = 'AL'
    BLOCK = 'BL'
