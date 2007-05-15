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

"""Client
This module contains classes that clients should use in order to make use
of the library.

Ideally you would inherit from the L{Client} class and override the
abstract methods."""

__version__ = "$Id$"

import logging
import gobject

import protocol
import transport
import structure
import msnp2p
import consts
from consts import PresenceStatus

logger = logging.getLogger('client')

class UserProfile(gobject.GObject):
    """User profile related informations.
    
        @undocumented: do_get_property, do_set_property"""
    
    __gproperties__ = {
            "passport": (gobject.TYPE_STRING,
                "Passport",
                "Passport account used for MSN : steevy.ball@hotmail.com",
                "",
                gobject.PARAM_READABLE),
            
            "password": (gobject.TYPE_STRING,
                "Password",
                "Password user for the account",
                "",
                gobject.PARAM_READABLE),

            "friendly-name":  (gobject.TYPE_STRING,
                "Friendly name",
                "A nickname that the user chooses to display to others",
                "",
                gobject.PARAM_READWRITE),

            "personal-message":  (gobject.TYPE_STRING,
                "Personal message",
                "The personal message that the user wants to display",
                "",
                gobject.PARAM_READWRITE),
            
            "profile": (gobject.TYPE_STRING,
                "Profile",
                "the text/x-msmsgsprofile sent by the server",
                "",
                gobject.PARAM_READWRITE),

            "presence":  (gobject.TYPE_STRING,
                "Presence",
                "The presence to show to others",
                "",
                gobject.PARAM_READWRITE)

            }

    def __init__(self, client, account):
        """Initializer
            
            @param client: the instance of L{Client} used to connect to this
                account
            @type client: L{Client}
            
            @param account: the user account
            @type account: (passport: string, password:string)"""
        gobject.GObject.__init__(self)
        self.__client = client
        self.__passport = account[0] 
        self.__password = account[1]
        self.__friendly_name = account[0]
        self.__personal_message = ""
        self.__presence = PresenceStatus.OFFLINE # current presence
        self.__profile = ""

    def __get_profile(self):
        return self.__profile
    profile = property(__get_profile,
        doc="The server profile for this account")
    
    def __set_friendly_name(self, friendly_name):
        self.__client._protocol.set_friendly_name(friendly_name)
    def __get_friendly_name(self):
        return self.__friendly_name
    friendly_name = property(__get_friendly_name, __set_friendly_name,
        doc="Friendly name to be shown to your contacts")
        
    def __set_presence(self, presence):
        self.__client._protocol.set_presence(presence)
    def __get_presence(self):
        return self.__presence
    presence = property(__get_presence, __set_presence,
        doc="User presence")

    def __set_personal_message(self, personal_message):
        self.__client._protocol.set_personal_message(personal_message)
    def __get_personal_message(self):
        return self.__personal_message
    personal_message = property(__get_personal_message, __set_personal_message,
        doc="User personal message")
        
    def do_get_property(self, pspec):
        if pspec.name == "passport":
            return self.__passport
        elif pspec.name == "password":
            return self.__password
        elif pspec.name == "friendly-name":
            return self.__friendly_name
        elif pspec.name == "personal-message":
            return self.__personal_message
        elif pspec.name == "presence":
            return self.__presence
        elif pspec.name == "profile":
            return self.__profile
        else:
            raise AttributeError, "unknown property %s" % pspec.name

    def do_set_property(self, pspec, value):
        if pspec.name == "friendly-name":
            self.__friendly_name = value
        elif pspec.name == "personal-message":
            self.__personal_message = value
        elif pspec.name == "presence":
            self.__presence = value
        elif pspec.name == "profile":
            self.__profile = value
        else:
            raise AttributeError, "unknown property %s" % pspec.name

class Client(object):
    """This class provides way to connect to the notification server as well
    as methods to manage the contact list, and the personnal settings.

    Basically you should inherit from this class and implement the callbacks
    in order to build a client.
    
    @group Connection: login, logout
    @group Contacts Management: *_contact
    @group Tags Management: *_tag
    @group Callbacks: on_*"""

    def __init__(self, server, account, proxies={},
            initial_status=consts.PresenceStatus.ONLINE):
        """Initializer

            @param server: the Notification server to connect to.
            @type server: tuple (hostname: string, port: integer)

            @param account: the account to use for authentication.
            @type account: tuple (passport: string, password: string)

            @param proxies: proxies that we can use to connect
            @type proxies: {type: string => L{gio.network.ProxyInfos}}

            @param initial_status: the initial status to login with
            @type initial_status: integer
            @see L{consts.PresenceStatus}"""        
        
        self.profile = UserProfile(self, account)
        self._transport = transport.DirectConnection(server)
        self._proxies = proxies
        
        self._protocol = protocol.NotificationProtocol(self, self._transport,
                self.profile, proxies)
        self._switchboards = []
        self._switchboards_callbacks = []

        self._transport.connect("connection-failure",
                self.on_connect_failure)
        self._transport.connect("connection-lost",
                self.on_disconnected)
        self._transport.connect("command-received",
                self.on_command_received)
        self._transport.connect("command-sent",
                self.on_command_sent)
        
        self._protocol.connect("login-failure",
                self.on_login_failure)
        self._protocol.connect("login-success",
                self.on_login_success)
        self._protocol.connect("mail-received",
                self.on_mail_received)
        self._protocol.connect("switchboard-invitation-received",
                self.on_switchboard_invitation)
        self._protocol.connect("switchboard-response-received",
                self.__on_switchboard_response_received)
        self._protocol.connect("notify::contactlist-status",
                self.__on_contact_list_status_change)
        self._protocol.connect("notify::contactlist-status",
                self.on_contact_list_status_change)
        self._protocol.connect("contactlist-tag-added",
                self.on_contact_list_tag_added)
        self._protocol.connect("contactlist-tag-renamed",
                self.on_contact_list_tag_renamed)
        self._protocol.connect("contactlist-tag-removed",
                self.on_contact_list_tag_removed)
        self._protocol.connect("contactlist-contact-received",
                self.on_contact_list_contact_received)
        self._protocol.connect("contactlist-contact-removed",
                self.on_contact_list_contact_removed)
        self._initial_status = initial_status

        self.p2p_transport_mgr = msnp2p.P2PTransportManager(self)
        self.slp_call_factory = msnp2p.SLPCallFactory(self)

    ### public methods & properties
    def login(self):
        """Login to the server."""
        self._transport.establish_connection()

    def logout(self):
        """Logout from the server."""
        for switchboard in self._switchboards:
            switchboard.leave_conversation()
        self._protocol.signoff()

    def add_tag(self, name):
        self._protocol.add_tag(name)
    add_tag.__doc__ = protocol.NotificationProtocol.add_tag.__doc__

    def remove_tag(self, guid):
        self._protocol.remove_tag(guid)
    remove_tag.__doc__ = protocol.NotificationProtocol.remove_tag.__doc__
        
    def rename_tag(self, guid, name):
        self._protocol.rename_tag(guid, name)        
    rename_tag.__doc__ = protocol.NotificationProtocol.rename_tag.__doc__

    def add_contact(self, passport, friendly_name):
        self._protocol.add_contact(passport, friendly_name)
    add_contact.__doc__ = protocol.NotificationProtocol.add_contact.__doc__

    def remove_contact(self, passport):
        self._protocol.remove_contact(passport)
    remove_contact.__doc__ = protocol.NotificationProtocol.remove_contact.__doc__

    def get_contact_by_passport(self, passport):
        """Return a L{protocol.Contact} instance for a given passport.
        
            @param passport: the passport of the contact.
            @type passport: string
            
            @return: the contact instance.
            @rtype: L{protocol.Contact}"""
        return self._protocol._get_contact_by_passport(passport)

    def get_contacts_by_list(self, list_type):
        """Return a mapping of passport to L{protocol.Contact} instance for
        a contacts in the given list.
        
            @param list_type: the privacy list (ALLOW, FORWARD ...)
            @type list_type: L{consts.List}
            
            @return: the contact instance.
            @rtype: dictionary (passport: string => contact:
                L{protocol.Contact})"""
        return self._protocol._get_contacts_by_list(list_type)
    
    ### internal Methods
    def _request_switchboard(self, callback):
        self._switchboards_callbacks.append(callback)
        self._protocol.request_switchboard()

    def __on_switchboard_response_received(self, proto, server, key):
        callback = self._switchboards_callbacks.pop(0)
        callback(server, key)
    
    def __on_contact_list_status_change(self, proto, prop):
        if self._protocol.get_property('contactlist-status') == \
                consts.ContactListStatus.SYNCHRONIZED:
            self._protocol.set_presence(self._initial_status)

    def _get_default_p2p_transport(self, peer):
        """ Called by P2PTransportManager. """
        return Conversation(self, [peer, ])

    ### Callbacks
    def on_connect_failure(self, transp):
        """Callback used when the connection to the server fails.
        
            @param transp: an instance of a class that implements the
                L{transport.BaseTransport} interface"""
        pass

    def on_disconnected(self, transp):
        """Callback used when we get disconnected from the server.
        
            @param transp: an instance of a class that implements the
                L{transport.BaseTransport} interface"""
        pass

    def on_command_received(self, transp, cmd):
        """Callback used when a command is received.
            
            @note: may be used for debugging purposes
            @param transp: an instance of a class that implements the
                L{transport.BaseTransport} interface
            @param cmd: a {structure.Command} instance"""
        pass

    def on_command_sent(self, transp, cmd):
        """Callback used when a command is sent.
            
            @note: may be used for debugging purposes
            @param transp: an instance of a class that implements the
                L{transport.BaseTransport} interface
            @param cmd: a {structure.Command} instance"""
        pass
    
    def on_login_success(self, proto):
        """Callback used when the login process succeeds.
        
            @param proto: the L{protocol.NotificationProtocol} instance"""
        pass
        
    def on_login_failure(self, proto):
        """Callback used when the login process fails.
        
            @param proto: the L{protocol.NotificationProtocol} instance"""
        pass

    def on_contact_list_status_change(self, proto, prop):
        """Callback used when the contact list status changes.
            
            @param proto: the L{protocol.NotificationProtocol} instance"""
        pass

    def on_contact_list_tag_added(self, proto, guid, name):
        """Callback used when a tag is added to the contact list.
            
            @param proto: the L{protocol.NotificationProtocol} instance
            @param guid: the tag unique identifier
            @param name: the tag name"""
        pass

    def on_contact_list_tag_renamed(self, proto, guid, name):
        """Callback used when a tag is renamed.
            
            @param proto: the L{protocol.NotificationProtocol} instance
            @param guid: the tag unique identifier
            @param name: the tag name"""
        pass

    def on_contact_list_tag_removed(self, proto, guid, name):
        """Callback used when a tag is removed from the contact list.
            
            @param proto: the L{protocol.NotificationProtocol} instance
            @param guid: the tag unique identifier
            @param name: the tag name"""
        pass

    def on_contact_list_contact_received(self, proto, passport, contact):
        """Callback used when a contact is received to the contact list.
            
            @param proto: the L{protocol.NotificationProtocol} instance
            @param passport: the contact passport
            @param contact: a L{protocol.Contact} instance"""
        pass
    
    def on_contact_list_contact_removed(self, proto, passport, contact):
        """Callback used when a contact is *completely* removed from the contact list,
        this means that it doesn't figure in any list anymore.
            
            @param proto: the L{protocol.NotificationProtocol} instance
            @param passport: the contact passport
            @param contact: a L{protocol.Contact} instance"""
        pass

    def on_mail_received(self, proto, server_message):
        """Callback used when a mail is received in the mailbox.
            
            @param proto: the L{protocol.NotificationProtocol} instance
            @param server_message: a L{structure.IncomingMessage} instance"""
        pass
    
    def on_switchboard_invitation(self, proto, server, key,
            session, passport, friendly_name):
        """Callback used when a contact invites us for conversation.
            
            @param proto: the L{protocol.NotificationProtocol} instance
            
            @param server: the server to connect to
            @type server: tuple (host: string, port: integer)
            
            @param key: the key used to authenticate to server when connecting
            @type key: string
            
            @param session: the session to join
            @type session: string
            
            @param passport: the passport of the inviter
            @type passport: string

            @param friendly_name: the friendly name of the inviter
            @type friendly_name: string"""
        pass

class Conversation(msnp2p.P2PTransport):
    """This class provides way to connect to the switchboard server.
    
        @group Callbacks: on_*"""

    MAX_MESSAGE_BODY_SIZE = 1254
    
    def __init__(self, client, invitee, server=None, key="", session=""):
        """Switchboard server connection initialization.

            @param client: the instance of L{Client} used for this account
            @type client: L{Client}

            @param invitee: a list of L{protocol.Contact} to invite, or the
                contact that invited us
            @type invitee: tuple (L{protocol.Contact}, L{protocol.Contact}, ...)
            
            @param server: the server to connect to
            @type server: tuple (hostname: string ,port: integer)
            
            @param key: the key used to authenticate to server when
                connecting
            @type key: string
            
            @param session: the session to join
            @type session: string
        """
        self._proxies = client._proxies

        self._switchboard = None
        self._transport = None
        self._client = client

        self.__invitee = invitee
        self.__pending_actions = []
        self.__switchboard_handler = []

        msnp2p.P2PTransport.__init__(self, client)

        if server is not None: # being invited
            assert(key != "")
            assert(session != "")
            self.__invitee = []
            self._transport = transport.DirectConnection(server)
            self._switchboard = protocol.SwitchboardProtocol(self._client,
                    self._transport, [], key, session, client._proxies)
            self.__attach_switchboard()
        else: # invite someone
            assert(invitee)
        self.__requested_sb = False

        gobject.idle_add(self.__connect)

    # Public methods
    def send_text_message(self, text):
        """Build and send a text message to all persons in this
        switchboard.
        
            @param text: the text message to send.
            @type text: string"""
        self.__queue_action(self._do_send_text_message, text)

    def invite_user(self, passport):
        """Request a contact to join in the conversation.
            
            @param passport: the passport of the contact to invite."""
        self.__queue_action(self._do_invite_user, passport)

    def leave_conversation(self):
        """Leave the conversation."""
        #:TODO: only when connected ?
        if self._switchboard:
            self._switchboard.leave_conversation()
        self._client._unregister_switchboard(self)
    
    # 
    def _do_invite_user(self, passport):
        contact = self._client.get_contact_by_passport(passport)
        assert(contact is not None)
        self._switchboard.invite_user(contact)

    def _do_send_text_message(self, text):
        msg = structure.OutgoingMessage(self._transport.transaction_id,
                consts.MessageAcknowledgement.HALF)
        msg.content_type = ("text/plain","UTF-8")
        msg.body = text.encode('UTF-8')
        self._switchboard.send_message(msg)

    ### events
    def on_message_received(self, switchboard, message):
        """callback used when a message is received.
            
            @param switchboard: the switchboard from where this message was
                received.
            @type switchboard: L{protocol.SwitchboardProtocol}
            
            @param message: the received message.
            @type message: L{structure.IncomingMessage}"""
        pass

    def on_user_typing(self, switchboard, contact):
        """callback used when a typing notification is received.
            
            @param switchboard: the switchboard from where this message was
                received.
            @type switchboard: L{protocol.SwitchboardProtocol}

            @param contact: the contact that joined in.
            @type contact: L{protocol.Contact}"""

    def on_user_joined(self, switchboard, contact):
        """callback used when a contact join the conversation.
            
            @param switchboard: the switchboard from where this message was
                received.
            @type switchboard: L{protocol.SwitchboardProtocol}

            @param contact: the contact that joined in.
            @type contact: L{protocol.Contact}"""
        pass

    def on_user_left(self, switchboard, contact):
        """callback used when a contact leaves the conversation.
            
            @param switchboard: the switchboard from where this message was
                received.
            @type switchboard: L{protocol.SwitchboardProtocol}

            @param contact: the contact that left.
            @type contact: L{protocol.Contact}"""
        pass

    ### Internal Methods
    def __queue_action(self, action, *args):
        self.__pending_actions.append((action, args))
        self.__process_pending_actions()

    def __attach_switchboard(self):
        handler = self.__switchboard_handler
        connect = self._switchboard.connect
        handler.append(connect("notify::switchboard-status",
            self.__on_switchboard_status_change))
        handler.append(connect("user-left", self.__on_user_left))
        handler.append(connect("user-left", self.on_user_left))
        handler.append(connect("user-joined", self.__on_user_joined)) 
        handler.append(connect("user-joined", self.on_user_joined))
        handler.append(connect("message-received", self.__on_message_received))

    def __detach_switchboard(self):
        for handler in self.__switchboard_handler:
            self._switchboard.handler_disconnect(handler)
        self.__switchboard_handler = []
        self._switchboard = None
        self._transport = None
        self.__requested_sb = False

    def __connect(self):
        if self._transport is not None:
            self._transport.establish_connection()
        elif not self.__requested_sb:
            self.__requested_sb = True
            self._client._request_switchboard(self.__on_switchboard_response)
        return False

    def __process_pending_actions(self):
        if self._switchboard is not None:
            switchboard_status = \
                    self._switchboard.get_property("switchboard-status")
        else:
            switchboard_status = consts.SwitchboardStatus.CLOSED

        if switchboard_status == consts.SwitchboardStatus.OPENED:
            if len(self.__invitee) > 0:
                for invitee in self.__invitee:
                    self._switchboard.invite_user(invitee)
                return
            for action, args in self.__pending_actions:
                action(*args)
            self.__pending_actions = []
        elif switchboard_status == consts.SwitchboardStatus.CLOSED or\
                switchboard_status == consts.SwitchboardStatus.IDLE:
            gobject.idle_add(self.__connect)

    ### switchboard callbacks
    def __on_user_left(self, switchboard, contact):
        if len(self._switchboard.users) == 1: # last user
            self.__invitee = [ contact, ]
        self.emit("p2p-peers-changed")

    def __on_user_joined(self, switchboard, contact):
        if contact in self.__invitee:
            self.__invitee.remove(contact)
        self.emit("p2p-peers-changed")
        switchboard_status = self._switchboard.get_property("switchboard-status")
        if len(self.__invitee) == 0 and \
                switchboard_status == consts.SwitchboardStatus.OPENED:
            self.__process_pending_actions()

    def __on_switchboard_response(self, server, key):
        self._transport = transport.DirectConnection(server)
        self._switchboard = protocol.SwitchboardProtocol(self._client,
                self._transport, self.__invitee, key, "", self._proxies)
        self.__attach_switchboard()
        gobject.idle_add(self.__connect)

    def __on_switchboard_status_change(self, proto, prop):
        switchboard_status = self._switchboard.get_property("switchboard-status")

        if switchboard_status == consts.SwitchboardStatus.IDLE and \
                len(self._switchboard.users) > 0:
            self.__invitee = self._switchboard.users.keys()

        if switchboard_status == consts.SwitchboardStatus.CLOSED or \
                switchboard_status == consts.SwitchboardStatus.IDLE:
            self.__detach_switchboard()

        elif switchboard_status == consts.SwitchboardStatus.OPENED:
            self.__process_pending_actions()

    def __on_message_received(self, switchboard, message):
        if message.content_type[0] == "application/x-msnmsgrp2p":
            peer = self._client.get_contact_by_passport(message.passport)
            self.emit("p2p-chunk-received", peer, message.body)
        elif message.content_type[0] == 'text/x-msmsgscontrol':
            passport = message.passport
            contact = self._switchboard.users[passport]
            self.on_user_typing(switchboard, contact)
        elif message.content_type[0] == "text/plain":
            self.on_message_received(switchboard, message)

    ### P2PTransport
    def get_p2p_name(self):
        return "switchboard"

    def get_p2p_peers(self):
        if self._switchboard != None:
            peers = self._switchboard.users.keys()
        else:
            peers = None

        if not peers:
            peers = (self.__invitee[0],)

        return [self._client.get_contact_by_passport(peer) for peer in peers]

    def get_p2p_rating(self):
        return 0

    def get_p2p_max_chunk_size(self):
        """Gets the maximum chunk size, which does not include the number of
        bytes required by the transports own framing.
        
            @rtype: integer"""
        return self.MAX_MESSAGE_BODY_SIZE

    def send_p2p_chunk(self, peer, chunk, callback=None, cb_args=()):
        self.__queue_action(self.__do_send_p2p_chunk, peer, chunk, callback,
                cb_args)

    def __do_send_p2p_chunk(self, peer, chunk, callback, cb_args):
        msg = structure.OutgoingMessage(self._transport.transaction_id,
                                      consts.MessageAcknowledgement.MSNC)
        headers = msg.headers
        headers["Content-Type"] = "application/x-msnmsgrp2p"
        headers["P2P-Dest"] = peer.get_property("passport")
        msg.body = chunk

        our_cb_args = (peer, chunk, callback, cb_args)
        self._switchboard.send_message(msg, self.__on_p2p_chunk_sent,
                our_cb_args)

    def __on_p2p_chunk_sent(self, peer, chunk, user_callback, user_cb_args):
        self.emit("p2p-chunk-sent", peer, chunk)
        if user_callback:
            user_callback(*user_cb_args)
