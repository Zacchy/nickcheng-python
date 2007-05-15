# -*- coding: utf-8 -*-
#
# pymsn - a python client library for Msn
#
# Copyright (C) 2005-2006 Ali Sabil <ali.sabil@gmail.com>
# Copyright (C) 2005-2006 Ole André Vadla Ravnås <oleavr@gmail.com> 
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

"""Protocol
Protocol abstraction module

This module tries to abstract the msn protocol as much as possible so that we
can easily upgrade or change the protocol easily without disturbing the whole
library.

@group Protocol: NotificationProtocol, SwitchboardProtocol, PassportAuth
"""

__version__ = "$Id$"

import gobject
gobject.threads_init()

import logging
import urllib
import threading

import structure
import util
import consts
from consts import ContactListStatus, PresenceStatus, List, SwitchboardStatus
from errors import ProtocolError

logger = logging.getLogger('protocol')

class Contact(gobject.GObject):
    """Contact related informations
    
        @undocumented: do_get_property, do_set_property"""
    
    __gsignals__ =  {
            "added" : (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                ()),

            "added-me" : (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                ()),

            "removed" : (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                ()),
            
            "removed-me" : (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                ()),
            }
    __gproperties__ = {
            "passport":  (gobject.TYPE_STRING,
                "Passport",
                "The contact's passport account name.",
                "", gobject.PARAM_READABLE),
            "lists":     (gobject.TYPE_INT,
                "Lists",
                "The lists the contact is part of.",
                0, 15, 0, gobject.PARAM_READWRITE),
            "tags":    (object,
                "Tags",
                "The tags the contact is part of.",
                gobject.PARAM_READWRITE),
            "friendly-name":  (gobject.TYPE_STRING,
                "Friendly name",
                "The contact's friendly name aka alias.",
                "", gobject.PARAM_READWRITE),
            "guid":      (gobject.TYPE_STRING,
                "GUID",
                "The contact's GUID.",
                "", gobject.PARAM_READABLE),
            "presence":    (gobject.TYPE_STRING,
                "Presence",
                "The contact's presence.",
                PresenceStatus.OFFLINE, gobject.PARAM_READWRITE),
            "personal-message":       (gobject.TYPE_STRING,
                "Personal Message",
                "The contact's personal message.",
                "", gobject.PARAM_READWRITE),
            "clientid":  (gobject.TYPE_UINT64,
                "Client ID",
                "The contact's client id.",
                0, consts.UINT32_MAX, 0, gobject.PARAM_READWRITE),
            "msnobject": (gobject.TYPE_STRING,
                "MSNObject",
                "The contact's MSNObject.",
                "", gobject.PARAM_READWRITE),
            }
    
    def __init__(self, client, passport, lists, tags=[],
        friendly_name='', guid=''):
        """Initializer
            
            @param client: the instance of L{Client} used to connect to the
                account where this Contact exists.
            @type client: L{Client}

            @param passport: the contact passport
            @type passport: string
            
            @param lists: the lists that contain this contact
            @type lists: integer, OR values L{consts.List.code}
            
            @param tags: the tags where the contact exists
            @type tags: [tag-guid: string, ...]
            
            @param friendly_name: contact friendly name
            @type friendly_name: string
            
            @param guid: contact guid
            @type guid: string"""
        gobject.GObject.__init__(self)
        self._passport = passport
        self._lists = lists
        self._tags = set(tags)
        self._friendly_name = friendly_name
        self.__guid = guid
        self.__client = client
        
        self._presence = PresenceStatus.OFFLINE
        self._personal_message = ""
        self._clientid = 0
        self._msnobject = ""

    def __set_guid(self, guid):
        self.__guid = guid
        self.notify("guid")
    def __get_guid(self):
        return self.__guid
    _guid = property(__get_guid, __set_guid,
        doc="Used by the protocol Layer to update the guid")

    def __get_passport(self):
        return self._passport
    passport = property(__get_passport,
        doc="Passport of this contact")

    def __get_friendly_name(self):
        return self._friendly_name
    friendly_name = property(__get_friendly_name,
        doc="Friendly name of this contact")
        
    def __get_presence(self):
        return self._presence
    presence = property(__get_presence,
        doc="Contact's presence")

    def __get_personal_message(self):
        return self._personal_message
    personal_message = property(__get_personal_message,
        doc="Contact's personal message")

    ### Public methods

    def in_list(self, list_name):
        """Check if this contact is in the given list
            
            @param list_name: the list name
            @type list_name: string L{consts.List}"""
        return self._lists & List.code[list_name]

    def block(self):
        """Block this contact and forbid him from seeing our presence"""
        self.__client._protocol.block_contact(self._passport)

    def unblock(self):
        """Unblock this contact and allow him to see our presence"""
        self.__client._protocol.unblock_contact(self._passport)

    def accept(self):
        """Accept this contact if he is in the pending list"""
        self.__client._protocol.accept_contact(self._passport)
    
    def reject(self):
        """Reject this contact if he is in the pending list"""
        self.__client._protocol.reject_contact(self._passport)

    def remove(self):
        """Re;ove this contact from our contact list"""
        self.__client._protocol.remove_contact(self._passport)
        
    def _add_to_list(self, list_name):
        """Adds this contact to the given list, used by the protocol
        layer to update the informations.

            @param list_name: the list name
            @type list_name: string L{consts.List}"""
        if not self.in_list(List.REVERSE) and \
                list_name == List.REVERSE:
            self.emit("added-me")
        elif not self.in_list(List.FORWARD) and \
                list_name == List.FORWARD:
            self.emit("added")
        self._lists |= List.code[list_name]
        self.notify("lists")

    def _remove_from_list(self, list_name):
        """removes this contact from the given list, used by the protocol
        layer to update the informations.
            
            @param list_name: the list name
            @type list_name: string L{consts.List}"""
        if self.in_list(List.REVERSE) and \
                list_name == List.REVERSE:
            self.emit("removed-me")
        elif self.in_list(List.FORWARD) and \
                list_name == List.FORWARD:
            self.emit("removed")

        self._lists ^= List.code[list_name]
        self.notify("lists")
    
    def have_tag(self, tag_guid):
        """Check if this contact has the given tag
            
            @param tag_guid: the tag GUID
            @type tag_guid: string"""
        return tag_guid in self._tags
    
    def tag(self, tag_guid):
        """Adds this contact to the given tag
            
            @param tag_guid: the tag GUID
            @type tag_guid: string"""
        self.__client._protocol.tag_contact(self.__guid, tag_guid)
        
    def _tag(self, tag_guid):
        """Adds this contact to the given tag, used by the protocol
        layer to update the informations.
            
            @param tag_guid: the tag GUID
            @type tag_guid: string"""
        self._tags.add(tag_guid)
        self.notify("tags")

    def untag(self, tag_guid):
        """Removes this contact from the given tag
            
            @param tag_guid: the tag GUID
            @type tag_guid: string"""
        self.__client._protocol.untag_contact(self.__guid, tag_guid)

    def _untag(self, tag_guid):
        """Removes this contact from the given tag, used by the protocol
        layer to update the informations.

            
            @param tag_guid: the tag GUID
            @type tag_guid: string"""
        self._tags.remove(tag_guid)
        self.notify("tags")

    ### gobject properties
    
    def do_get_property(self, pspec):
        if pspec.name == "passport":
            return self._passport
        elif pspec.name == "lists":
            return self._lists
        elif pspec.name == "tags":
            return self._tags
        elif pspec.name == "friendly-name":
            return self._friendly_name
        elif pspec.name == "guid":
            return self.__guid
        elif pspec.name == "presence":
            return self._presence
        elif pspec.name == "personal-message":
            return self._personal_message
        elif pspec.name == "clientid":
            return self._clientid
        elif pspec.name == "msnobject":
            return self._msnobject
        else:
            raise AttributeError, "unknown property %s" % pspec.name

    def do_set_property(self, pspec, value):
        if pspec.name == "lists":
            self._lists = value
        elif pspec.name == "tags":
            self._tags = value
        elif pspec.name == "friendly-name":
            self._friendly_name = value
        elif pspec.name == "presence":
            self._presence = value
        elif pspec.name == "personal-message":
            self._personal_message = value
        elif pspec.name == "clientid":
            self._clientid = value
        elif pspec.name == "msnobject":
            self._msnobject = value
        else:
            raise AttributeError, "unknown property %s" % pspec.name

    
    def _update_presence(self, **details):
        self.freeze_notify()
        
        if "presence" in details:
            presence = details["presence"]
            if presence != self._presence:
                self.set_property("presence", presence)

        if "friendly_name" in details:
            friendly_name = details["friendly_name"]
            if friendly_name != self._friendly_name:
                self.set_property("friendly-name", friendly_name)

        if "personal_message" in details:
            personal_message = details["personal_message"]
            if personal_message != self._personal_message:
                self.set_property("personal-message", personal_message)
        
        if "clientid" in details:
            clientid = details["clientid"]
            if clientid != self._clientid:
                self.set_property("clientid", clientid)
        
        if "msnobject" in details:
            msnobject = details["msnobject"]
            if msnobject != self._msnobject:
                self.set_property("msnobject", msnobject)
        
        self.thaw_notify()
gobject.type_register(Contact)

class PassportAuth(gobject.GObject):
    """Passport authentication client.
    This class is used to handle the Tweener authentication process
        
    @undocumented: do_set_property, do_get_property"""

    __gproperties__ = {
        "username": (gobject.TYPE_STRING,
            "Username",
            "The passport username.",
            "",
            gobject.PARAM_READWRITE),

        "password": (gobject.TYPE_STRING,
            "Password",
            "The passport password.",
            "",
            gobject.PARAM_READWRITE),

        "challenge": (gobject.TYPE_STRING,
            "Challenge",
            "The passport challenge.",
            "",
            gobject.PARAM_READWRITE),
    }

    __gsignals__ = {
        "auth-success": (gobject.SIGNAL_RUN_FIRST,
            gobject.TYPE_NONE,
            (gobject.TYPE_STRING,)),

        "auth-failure": (gobject.SIGNAL_RUN_FIRST,
            gobject.TYPE_NONE,
            ()),
    }

    def __init__(self, username="", password="", challenge="", proxy=None):
        """Passport authentication client
        
            @param username: the passport of the person to connect
            @param password: the password used to autheticate
            @param challenge: the challenge string sent by the server
            @param proxy: a L{gio.network.ProxyInfos} instance with the
                https type
        """
        gobject.GObject.__init__(self)
        if proxy is not None:
            assert(proxy.type == 'https')
        self._username = username
        self._password = password
        self._challenge = challenge
        self._proxy = proxy
    
    def start(self):
        """Start authentication process"""
        threading.Thread(name="NexusAuth", target=self._auth_thread).start()

    def do_set_property(self, pspec, value):
        if pspec.name == "username":
            self._username = value
        elif pspec.name == "password":
            self._password = value
        elif pspec.name == "challenge":
            self._challenge = value
        else:
            raise AttributeError, "unknown property %s" % pspec.name

    def do_get_property(self, pspec):
        if pspec.name == "username":
            return self._username
        elif pspec.name == "password":
            return self._password
        elif pspec.name == "challenge":
            return self._challenge
        else:
            raise AttributeError, "unknown property %s" % pspec.name

    def _auth_thread(self):
        def _parse_header(values):
            return dict([pair.split("=", 1) for pair in values.split(",")])
        try:

            nexus = util.https_open(consts.PASSPORT_NEXUS, proxy = self._proxy)
            values = _parse_header(nexus.getheader("PassportURLs"))

            authentication_string = "Passport1.4 OrgVerb=GET"
            authentication_string += ",OrgURL=http%3A%2F%2Fmessenger%2Emsn%2Ecom"
            authentication_string += ",sign-in=" + urllib.quote(self._username)
            authentication_string += ",pwd=" + urllib.quote(self._password)
            authentication_string += "," + self._challenge
            login = util.https_open("https://" + values["DALogin"],
                    headers={"Authorization":authentication_string},
                    proxy = self._proxy)

            auth_info = login.getheader("Authentication-Info")
            if auth_info == None:
                # Wrong password?
                gobject.idle_add(self._emit_result, "auth-failure", ())
                return

            ticket = _parse_header(auth_info)["from-PP"][1:-1]

            gobject.idle_add(self._emit_result, "auth-success", (ticket,))
        except util.HTTPException:
            gobject.idle_add(self._emit_result, "auth-failure", ())
            return
        except KeyError:
            gobject.idle_add(self._emit_result, "auth-failure", ())
            return

    def _emit_result(self, signal, args):
        self.emit(signal, *args)
        return False
gobject.type_register(PassportAuth)

class NotificationProtocol(gobject.GObject):
    """NotificationProtocol
    Notification protocol absraction.
    
        @undocumented: do_get_property, do_set_property
        @group Informations: set_personal_message, set_friendly_name, set_presence
        @group Contacts: *_contact
        @group Tags: *_tag"""

    __gsignals__ = {
            "login-failure" : (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                ()),

            "login-success" : (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                ()),

            "mail-received" : (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                (object,)),

            "switchboard-response-received" : (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                (object,gobject.TYPE_STRING)),

            "switchboard-invitation-received" : (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                (object,gobject.TYPE_STRING, gobject.TYPE_STRING,
                    gobject.TYPE_STRING, gobject.TYPE_STRING)),

            "contactlist-tag-added" : (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                (object, object)),

            "contactlist-tag-renamed" : (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                (object, object)),

            "contactlist-tag-removed" : (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                (object, object)),

            "contactlist-contact-received" : (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                (object, object)),

            "contactlist-contact-removed" : (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                (object, object)),
            }

    __gproperties__ = {
            "contactlist-status":  (gobject.TYPE_INT,
                "Contact list status",
                "The status of the contact list.",
                0, 2, ContactListStatus.NOT_SYNCHRONIZED,
                gobject.PARAM_READABLE)
            }

    def __init__(self, client, transport, profile, proxies={}):
        """Initializer

            @param client: the parent instance of L{client.Client}
            @type client: L{client.Client}

            @param transport: The transport to use to speak the protocol
            @type transport: L{transport.BaseTransport}
            
            @param profile: a L{client.UserProfile} instance
            @type profile: L{client.UserProfile}
            @param proxies: a dictonary mapping the proxy type to a
                gio.network.ProxyInfos instance
            @type proxies: {type: string, proxy:L{gio.network.ProxyInfos}}
        """
        gobject.GObject.__init__(self)
        transport.connect("command-received", self.__dispatch_command )
        transport.connect("connection-success", self.__connect_cb)
        transport.connect("connection-failure", self.__disconnect_cb)
        transport.connect("connection-lost", self.__disconnect_cb)

        self.__client = client
        self.__transport = transport
        self.__profile = profile
        self._proxies = proxies
        self._tags = {}
        self._contacts = {}

        self.__contact_list_status = ContactListStatus.NOT_SYNCHRONIZED

    def do_get_property(self, pspec):
        if pspec.name == "contactlist-status":
            return self.__contact_list_status
        else:
            raise AttributeError, "unknown property %s" % pspec.name

    def do_set_property(self, pspec, value):
        raise AttributeError, "unknown property %s" % pspec.name

    def _default_handler(self, command):
        """
        Default handler used when no handler is defined
        
            @param command: the received command
            @type command: L{structure.Command}
        """
        logger.warning('Notification unhandled command :' + repr(command))

    def _error_handler(self, error):
        """Handles errors
        
            @param error: an error command object
            @type error: L{structure.Command}
        """
        logger.error('Notification got error :' + repr(error))

    ### Public Methods
    def set_presence(self, presence):
        """Publish the new user presence.

            @param presence: the new presence
            @type presence: string L{consts.PresenceStatus}
        """
        if presence == PresenceStatus.OFFLINE:
            return self.signoff()
        self.__transport.send_command_ex('CHG',
                (presence, str(consts.ID)))
    
    def set_friendly_name(self, friendly_name):
        """Sets the new friendly name
            
            @param friendly_name: the new friendly name
            @type friendly_name: string"""
        self.__transport.send_command_ex('PRP',
                ('MFN', urllib.quote(friendly_name)))

    def set_personal_message(self, personal_message=''):
        """Sets the new personal message
            
            @param personal_message: the new personal message
            @type personal_message: string"""
        xml = util.Xml()
        message = xml.escape(personal_message)
        pm = '<Data><PSM>%s</PSM><CurrentMedia></CurrentMedia></Data>'% message
        self.__transport.send_command_ex('UUX',
                payload=pm)
    
    def request_switchboard(self):
        """Request a switchboard in order to open a new conversation"""
        self.__transport.send_command_ex('XFR', ('SB',))

    def signoff(self):
        """Logout from the server"""
        self.__transport.send_command_ex('OUT')
        self.__transport.lose_connection()

    def add_tag(self, name):
        """Create a new tag using the given name
            
            @param name: the tag name"""
        self.__transport.send_command_ex('ADG',
                (urllib.quote(name), '0'))

    def remove_tag(self, guid):
        """Remove a tag given its GUID
            
            @param guid: the guid of the tag to remove
            @type guid: string"""
        self.__transport.send_command_ex('RMG',
                (guid,))

    def rename_tag(self, guid, name):
        """Renames a tag
            
            @param guid: the guid of the tag to rename
            @type guid: string
            
            @param name: the new tag name"""

        self.__transport.send_command_ex('REG',
                (guid, urllib.quote(name), '0'))


    def add_contact(self, passport, friendly_name):
        """Add a contact to the contact list
        
            @param passport: the passport of the contact to add
            @param friendly_name: the friendly name of the contact to add"""
        contact = self._get_contact_by_passport(passport)
        if contact and contact.in_list(List.FORWARD):
            return
        self.__transport.send_command_ex('ADC',
                (List.FORWARD, 'N=%s' % passport, 'F=%s' % friendly_name))
    
    def accept_contact(self, passport):
        """Accept a contact and allow him to see our presence status
        
            @param passport: the passport of the contact to accept"""
        self.unblock_contact(passport)
        self.__transport.send_command_ex('ADC',
                (List.REVERSE, 'N=%s' % passport))
        self.__transport.send_command_ex('REM',
                (List.PENDING, 'N=%s' % passport))
    
    def reject_contact(self, passport):
        """Reject a contact and forbid him from seeing our presence status
        
            @param passport: the passport of the contact to reject"""
        self.block_contact(passport)
        self.__transport.send_command_ex('REM',
                (List.PENDING, passport))
        
    def remove_contact(self, passport):
        """Remove a contact from our contact list
        
            @param passport: the passport of the contact to accept"""
        contact = self._get_contact_by_passport(passport)
        if not (contact and contact.in_list(List.FORWARD)):
            return
        #:TODO: remove contact from all tags ?
        self.__transport.send_command_ex('REM',
                (List.FORWARD, contact.get_property("guid")))

    def tag_contact(self, contact_guid, tag_guid):
        """Tag a contact with a given tag
            
            @param contact_guid: the contact to tag
            @param tag_guid: the tag where the contact will be put"""
        assert(tag_guid in self._tags)
        #:TODO: make check in contact_guid
        self.__transport.send_command_ex('ADC',
                (List.FORWARD, 'C=%s' % contact_guid, tag_guid))

    def untag_contact(self, contact_guid, tag_guid):
        """Untag a contact from a give tag
                        
            @param contact_guid: the contact to tag
            @param tag_guid: the tag from where the contact will be removed"""
        assert(tag_guid in self._tags)
        #:TODO: make check in contact_guid
        self.__transport.send_command_ex('REM',
                (List.FORWARD, contact_guid, tag_guid))       

    def block_contact(self, passport):
        """Block a contact and forbid him from seeing our presence status
        
            @param passport: the passport of the contact to block"""

        contact = self._get_contact_by_passport(passport)
        if contact and contact.in_list(List.ALLOW):
            self.__transport.send_command_ex('REM',
                    (List.ALLOW, 'N=%s' % passport))

        self.__transport.send_command_ex('ADC',
                (List.BLOCK, 'N=%s' % passport))

    def unblock_contact(self, passport):
        """Unblock a contact and allow him to see our presence status
        
            @param passport: the passport of the contact to unblock"""

        contact = self._get_contact_by_passport(passport)
        if contact and contact.in_list(List.BLOCK):
            self.__transport.send_command_ex('REM',
                    (List.BLOCK, 'N=%s' % passport))

        self.__transport.send_command_ex('ADC', (List.ALLOW, 'N=%s' % passport))

    # Connection ---------------------------------------------------------
    def _handle_VER(self, command):
        if len(command.arguments[:-1]) == 0:
            raise ProtocolError('Invalid VER response : ' + command)
        self.__transport.send_command_ex('CVR', consts.CVR + \
                (self.__profile.get_property('passport'),))

    def _handle_CVR(self, command):
        self.__transport.send_command_ex('USR',
                ('TWN', 'I', self.__profile.get_property('passport')))

    def _handle_USR(self, command):
        args_len = len(command.arguments)
        # MSNP11 have only 4 params for final USR
        if args_len != 3 and args_len != 4:
            err = "Receiver USR with invalid number of params : " + str(command)
            raise ProtocolError(err)

        if command.arguments[0] == "OK":
            self.emit("login-success")
        # we need to obtain auth from a passport server
        elif command.arguments[1].upper() == "S":
            passport = self.__profile.get_property("passport")
            password = self.__profile.get_property("password")
            challenge = command.arguments[2]
            
            proxy = None
            if 'https' in self._proxies:
                proxy = self._proxies['https']

            auth = PassportAuth(passport, password, challenge, proxy)
            auth.connect("auth-success", self.__auth_success_cb)
            auth.connect("auth-failure", self.__auth_failure_cb)
            auth.start()

    def _handle_XFR(self, command):
        if command.arguments[0] == 'NS':
            try:
                host, port = command.arguments[1].split(':')
                port = int(port)
            except ValueError:
                host = command.arguments[1]
                port = self.__transport.server[1]
            logger.debug('<-> Redirecting to ' + command.arguments[1])
            self.__transport.reset_connection((host,port))
        else: # connect to a switchboard
            host, port = command.arguments[1].split(':',1)
            port = int(port)
            key = command.arguments[3]
            self.emit("switchboard-response-received", (host,port), key)

    def _handle_SBS(self, command): # unknown command
        pass

    def _handle_OUT(self, command):
        self.__profile.set_property("presence", PresenceStatus.OFFLINE)

    # Messages -----------------------------------------------------------
    def _handle_MSG(self, command):
        msg = structure.IncomingMessage(command)
        if msg.content_type[0] == 'text/x-msmsgsprofile':
            self.__profile._profile = command
            
            self.__transport.send_command_ex( 'SYN', ('0', '0') )
            self.__contact_list_status = ContactListStatus.SYNCHRONIZING
            self.notify("contactlist-status")
            
        elif msg.content_type[0] in \
                ('text/x-msmsgsinitialemailnotification', \
                 'text/x-msmsgsemailnotification'):
            self.emit("mail-received", msg)

    def _handle_PRP(self,command):
        ctype = command.arguments[0]
        if len(command.arguments) < 2: return
        if ctype == 'MFN':
            self.__profile.set_property('friendly-name',
                    urllib.unquote(command.arguments[1]))
        # TODO: add support for other stuff

    # Invitations --------------------------------------------------------
    def _handle_RNG(self,command):
        host, port = command.arguments[1].split(':',1)
        port = int(port)
        session = command.arguments[0]
        key = command.arguments[3]
        passport = command.arguments[4]
        friendly_name = urllib.unquote(command.arguments[5])
        self.emit("switchboard-invitation-received", (host,port), key,
                session, passport, friendly_name)
                                    
    # Buddies ------------------------------------------------------------
    def _handle_SYN(self,command):
        self.remaining_contacts = int(command.arguments[2])

    def _handle_LSG(self,command): # list group
        name = urllib.unquote(command.arguments[0])
        guid = command.arguments[1]
        self._tags[guid] = name
        self.emit("contactlist-tag-added", guid, name)

    def _handle_LST(self,command): # list contact
        self.remaining_contacts -= 1
        infos = self.__ADC_infos(command.arguments)
        contact = Contact(self.__client, infos['passport'],
                infos['lists'],
                infos['tags'],
                infos['friendly-name'],
                infos['guid'])
        self._contacts[infos['passport']] = contact
        self.emit("contactlist-contact-received", infos['passport'], contact)
        if self.remaining_contacts <= 0:
            del(self.remaining_contacts)
            self.__contact_list_status = ContactListStatus.SYNCHRONIZED
            self.notify("contactlist-status")

    def _handle_BPR(self,command): # contact infos
        pass

    def _handle_SBP(self,command): # contact saved Friendly name 
        pass

    def _handle_UBX(self,command): # contact infos
        contact = self._get_contact_by_passport(command.arguments[0])
        if command.payload:
            xml = util.Xml()
            data = xml.parse(text = command.payload)
            contact.set_property("personal-message", data.PSM.get_content())

    def _handle_ADG(self,command):
        name = urllib.unquote(command.arguments[0])
        guid = command.arguments[1]
        self._tags[guid] = name
        self.emit("contactlist-tag-added", guid, name)

    def _handle_RMG(self,command):
        guid = command.arguments[1]
        name = self._tags[guid]
        del self._tags[guid]
        self.emit("contactlist-tag-removed", guid, name)

    def _handle_REG(self,command):
        name = urllib.unquote(command.arguments[0])
        guid = command.arguments[1]
        self._tags[guid] = name
        self.emit("contactlist-tag-renamed", guid, name)
    
    def _handle_ADC(self, command):
        infos = self.__ADC_infos(command.arguments[1:])
        if command.arguments[0] == List.FORWARD:
            contact = self._get_contact_by_passport(infos['passport'])
            if contact is None: # Completely new contact
                contact = Contact(self.__client, infos['passport'],
                        infos['lists'],
                        infos['tags'],
                        infos['friendly-name'],
                        infos['guid'])
                self._contacts[infos['passport']] = contact
                self.emit('contactlist-contact-received', infos['passport'], contact)
            else:
                contact._guid = infos['guid']
                contact.set_property('friendly-name', infos['friendly-name'])
                for tag in infos['tags']:
                    contact._tag(tag)
                contact._add_to_list(List.FORWARD) 
        elif command.arguments[0] == List.REVERSE:
            contact = self._get_contact_by_passport(infos['passport'])
            if contact is None:
                contact = Contact(self.__client, infos['passport'],
                        infos['lists'],
                        infos['tags'],
                        infos['friendly-name'],
                        infos['guid'])
                self._contacts[infos['passport']] = contact
                self.emit("contactlist-contact-received", infos['passport'], contact)
            else:
                contact._add_to_list(List.REVERSE)
                contact.set_property('friendly-name', infos['friendly-name'])
        elif command.arguments[0] == List.ALLOW:
            contact = self._get_contact_by_passport(infos['passport'])
            contact._add_to_list(List.ALLOW)
        elif command.arguments[0] == List.BLOCK:
            contact = self._get_contact_by_passport(infos['passport'])
            contact._add_to_list(List.BLOCK)

    def _handle_REM(self, command):
        args = command.arguments
        if args[0] == List.FORWARD:
            contact = self._get_contact_by_guid(args[1])
            assert(contact != None)
            passport = contact.get_property("passport")
            if len(args) == 2: # remove completely
                contact._remove_from_list(List.FORWARD)
                if contact.get_property("lists") == 0:
                    self.emit("contactlist-contact-removed", passport, contact)
                    del self._contacts[passport]
            else: # remove from a group
                contact._untag(args[2])
        else:
            contact = self._get_contact_by_passport(args[1])
            contact._remove_from_list(args[0])

    # Statuses -----------------------------------------------------------------
    def _handle_CHG(self,command):
        self.__profile.set_property("presence", command.arguments[0])

    def _handle_ILN(self,command):
        self._handle_NLN(command)

    def _handle_FLN(self,command):
        c = self._get_contact_by_passport(command.arguments[0])
        c.set_property("presence", PresenceStatus.OFFLINE)

    def _handle_NLN(self,command):
        c = self._get_contact_by_passport(command.arguments[1])
        friendly_name = command.arguments[2]
        guid = c.get_property('guid')
        if len(command.arguments) > 4:
            msnobject = urllib.unquote(command.arguments[4])
        else:
            msnobject = ""
        
        c._update_presence(presence=command.arguments[0],
                friendly_name=urllib.unquote(friendly_name),
                msnobject=msnobject)

        if friendly_name:
            self.__transport.send_command_ex('SBP', (guid, 'MFN', friendly_name ))

    # Pings --------------------------------------------------------------------
    def _handle_QNG(self,command):
        pass

    def _handle_QRY(self,command):
        pass

    def _handle_CHL(self,command):
        response = util.compute_challenge(command.arguments[0])
        self.__transport.send_command_ex('QRY',(consts.PRODUCT_ID,),payload=response)
    
    def __ADC_infos(self, args):
        result = {
                    'passport' : '', 'friendly-name' : '', 'guid' : '',
                    'lists' : 0, 'tags' : ()
                 }
        for i in args:
            if i[0:2] == 'N=': result['passport'] = i[2:] 
            elif i[0:2] == 'F=': result['friendly-name'] = urllib.unquote(i[2:]) 
            elif i[0:2] == 'C=': result['guid'] = i[2:] 
            else:
                try: result['lists'] = int(i)
                except ValueError: 
                    result['tags'] = i.split(',')
        return result
    
    def _get_contact_by_guid(self, guid):
        for passport, contact in self._contacts.iteritems():
            if contact.get_property("guid") == guid:
                return contact
        return None
    
    def _get_contact_by_passport(self, passport):
        if passport in self._contacts:
            return self._contacts[passport]
        return None

    def _get_contacts_by_list(self, list_type):
        contacts = {}
        for passport, contact in self._contacts.iteritems():
            if contact.in_list(list_type):
                contacts[passport] = contact
        return contacts

    def __dispatch_command(self, connection, command):
        if not command.is_error():
            handler = getattr(self,
                    '_handle_' + command.name,
                    self._default_handler)
            handler(command)
        else:
            self._error_handler(command)
   
    def __connect_cb(self, transport):
        self.__transport.send_command_ex( 'VER', consts.VER )

    def __disconnect_cb(self, transport):
        presence = self.__profile.get_property("presence")
        if presence != PresenceStatus.OFFLINE:
            self.__profile.set_property("presence", PresenceStatus.OFFLINE)

    def __auth_success_cb(self, auth, ticket):
        self.__transport.send_command_ex( 'USR', ('TWN','S',ticket) )

    def __auth_failure_cb(self, auth):
        self.emit("login-failure")

gobject.type_register(NotificationProtocol)

class SwitchboardProtocol(gobject.GObject):
    """Switchboard Protocol abstraction

    @undocumented: do_set_property, do_get_property"""

    __gsignals__ = {
            "message-received": (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                (object,)),
            
            "message-sent": (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                (object,)),

            "message-delivered": (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                (object,)),

            "message-undelivered": (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                (object,)),

            "user-joined": (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                (object,)),

            "user-left": (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                (object,))
    }
    __gproperties__ = {
            "key": (gobject.TYPE_STRING,
                "Authentication Key",
                "The authentication key.",
                "", gobject.PARAM_READWRITE),

            "session": (gobject.TYPE_STRING,
                "Switchboard Session",
                "The switchboard session to join.",
                "", gobject.PARAM_READWRITE),

            "switchboard-status":  (gobject.TYPE_INT,
                "Switchboard status",
                "The status of the contact list.",
                0, 7, SwitchboardStatus.CLOSED,
                gobject.PARAM_READABLE)

            }

    def __init__(self, client, transport, invitee=[], key="", session="", proxies={}):
        """initializer

            @param client: the instance of L{client.Client} that is making use
                of this Switchboard
            @type client: L{client.Client}

            @param transport: The transport to use to speak the protocol
            @type transport: L{transport.BaseTransport}

            @param invitee: a list of contacts to invite
            @type invitee: tuple (L{Contact}, L{Contact}, ...)
            
            @param key: the key used to authenticate to server when
                connecting
            @type key: string
            
            @param session: the session to join
            @type session: string
            
            @param proxies: proxies that we can use to connect
            @type proxies: {type: string => L{gio.network.ProxyInfos}}"""
        gobject.GObject.__init__(self)
        transport.connect("command-received", self.__dispatch_command)
        transport.connect("connection-success", self.__connect_cb)
        transport.connect("connection-failure", self.__disconnect_cb)
        transport.connect("connection-lost", self.__disconnect_cb)

        self.__client = client
        self.__transport = transport
        self.__key = key
        self.__invitee = invitee
        self.__session = session
        self.__status = SwitchboardStatus.CLOSED
        self._proxies = proxies
        self.users = {}

    def __del__(self):
        self.__client.switchboards.remove(self)

    def _default_handler(self, command):
        """Default handler used when no handler is defined
        
            @param command: the received command
            @type command: L{structure.Command}
        """
        logger.warning('Switchboard unhandled command :' + str(command)[:-2])

    def _error_handler(self, error):
        """Handles errors
        
            @param error: an error command object
            @type error: L{structure.Command}
        """
        logger.error('Switchboard got error :' + str(error)[:-2])
    
    ### Public API
    def invite_user(self, contact):
        """Invite user to join in the conversation
            
            @param contact: the contact to invite
            @type contact: L{Contact}"""
        assert(self.__status == SwitchboardStatus.OPENING or \
                self.__status == SwitchboardStatus.OPENED)
        self.__transport.send_command_ex('CAL', (contact.get_property("passport"),) )

    def send_message(self, message, callback=None, cb_args=()):
        """Send a message to all contacts in this switchboard
        
            @param message: the message to send
            @type message: L{structure.OutgoingMessage}"""
        assert(self.__status == SwitchboardStatus.OPENED)
        our_cb_args = (message, callback, cb_args)
        self.__transport.send_command(message, callback=self.__on_message_sent, cb_args=our_cb_args)

    def __on_message_sent(self, message, user_callback, user_cb_args):
        self.emit("message-sent", message)
        if user_callback:
            user_callback(*user_cb_args)

    def leave_conversation(self):
        """Leave the conversation"""
        assert(self.__status == SwitchboardStatus.OPENED)
        self.__transport.send_command_ex('OUT')

    ### GObject properties

    def do_get_property(self, pspec):
        if pspec.name == "key":
            return self.__key
        elif pspec.name == "session":
            return self.__session
        elif pspec.name == "switchboard-status":
            return self.__status
        else:
            raise AttributeError, "unknown property %s" % pspec.name

    def do_set_property(self, pspec, value):
        if pspec.name == "key":
            self.__key = value
        elif pspec.name == "session":
            self.__session = value
        else:
            raise AttributeError, "unknown property %s" % pspec.name

    ### Command Handlers
    def _handle_ANS(self, command):
        if command.arguments[0] == 'OK':
            self.__set_switchboard_status(SwitchboardStatus.OPENED)
        else:
            self.__set_switchboard_status(SwitchboardStatus.AUTHENTICATED)

    def _handle_USR(self, command):
        self.__set_switchboard_status(SwitchboardStatus.AUTHENTICATED)
        self.__set_switchboard_status(SwitchboardStatus.OPENING)
        for invitee in self.__invitee:
            self.invite_user(invitee)
        
    def _handle_IRO(self, command):
        if command.arguments[0] == '1':
            self.__set_switchboard_status(SwitchboardStatus.OPENING)
        passport = command.arguments[2]
        friendly_name = urllib.unquote(command.arguments[3])
        contact = self.__client.get_contact_by_passport(passport)
        if contact is None:
            contact = Contact(self.__client, passport, 0, friendly_name=friendly_name)
        self.users[passport] = contact
        self.emit("user-joined", contact)

    def _handle_JOI(self, command):
        passport = command.arguments[0]
        friendly_name = urllib.unquote(command.arguments[1])
        contact = self.__client.get_contact_by_passport(passport)
        if contact is None:
            contact = Contact(self.__client, passport, 0, friendly_name=friendly_name)
        self.users[passport] = contact
        if passport in self.__invitee:
            self.__invitee.remove(passport)
        self.emit("user-joined", contact)
        if len(self.__invitee) == 0:
            self.__set_switchboard_status(SwitchboardStatus.OPENED)

    def _handle_BYE(self, command):
        if len(command.arguments) == 1:
            passport = command.arguments[0]
            self.emit("user-left", self.users[passport])
            del self.users[passport]
        else:
            self.__set_switchboard_status(SwitchboardStatus.IDLE)
            self.users = {}

    def _handle_OUT(self, command):
        pass

    def _handle_MSG(self, command):
        msg = structure.IncomingMessage(command)
        self.emit("message-received", msg)
        
    def _handle_ACK(self, command):
        self.emit("message-delivered", command)

    def _handle_NAK(self, command):
        self.emit("message-undelivered", command)

    ### Private Methods
    def __dispatch_command(self, connection, command):
        if not command.is_error():
            handler = getattr(self,
                    '_handle_' + command.name,
                    self._default_handler)
            handler(command)
        else:
            self._error_handler(command)
    
    def __set_switchboard_status(self, status):
        if status == SwitchboardStatus.CLOSED and \
                self.__status == SwitchboardStatus.IDLE:
            return
        self.__status = status
        self.notify("switchboard-status")

    def __connect_cb(self, transport):
        self.__set_switchboard_status(SwitchboardStatus.CONNECTED)
        passport = self.__client.profile.get_property("passport")

        if self.__session:
            arguments = (passport, self.__key, self.__session)
            self.__transport.send_command_ex('ANS', arguments )
        else:
            arguments = (passport, self.__key) 
            self.__transport.send_command_ex('USR', arguments)
        self.__set_switchboard_status(SwitchboardStatus.AUTHENTICATING)

    def __disconnect_cb(self, transport):
        self.__set_switchboard_status(SwitchboardStatus.CLOSED)

gobject.type_register(SwitchboardProtocol)

