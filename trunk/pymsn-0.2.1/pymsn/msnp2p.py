# -*- coding: utf-8 -*-
#
# pymsn - a python client library for Msn
#
# Copyright (C) 2006  Ole André Vadla Ravnås <oleavr@gmail.com>
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""msnp2p
Handles the msnp2p protocol used by the core msn protocol for display pictures,
custom smileys and file transferts."""

__version__ = "$Id$"

import random
import sys
import gobject
import struct
import cStringIO as StringIO
import logging
from base64 import standard_b64encode, standard_b64decode

import util
import consts
from errors import ParseError, ProtocolError, SLPError

logger = logging.getLogger('msnp2p')

CALL_HANDLERS = {}

status_message = {
    200 : "200 OK",
    404 : "404 Not Found",
    500 : "500 Internal Error",
    603 : "603 Decline",
}

P2P_SESSION_ID        = 0
P2P_MESSAGE_ID        = 1
P2P_DATA_OFFSET       = 2
P2P_DATA_SIZE         = 3
P2P_CHUNK_SIZE        = 4
P2P_FLAGS             = 5
P2P_ACKED_MSG_ID      = 6
P2P_PREV_ACKED_MSG_ID = 7
P2P_ACKED_DATA_SIZE   = 8
P2P_APP_ID            = 9

P2P_FLAGS_NONE      = 0x00000000
P2P_FLAGS_ACK       = 0x00000002
P2P_FLAGS_ERROR     = 0x00000008
P2P_FLAGS_DATA      = 0x00000020
P2P_FLAGS_FTDATA    = 0x01000030

EUF_GUID_MSNOBJECT = "{A4268EEC-FEC5-49E5-95C3-F126696BDBF6}"

SLP_SESSION_REQ_CONTENT_TYPE = "application/x-msnmsgr-sessionreqbody"
SLP_SESSION_CLOSE_CONTENT_TYPE = "application/x-msnmsgr-sessionclosebody"

SLP_TRANSFER_REQ_CONTENT_TYPE = "application/x-msnmsgr-transreqbody"
SLP_TRANSFER_RESP_CONTENT_TYPE = "application/x-msnmsgr-transrespbody"


def generate_guid():
    """
    Generate a time and space guid (version 1 uuid)
    according to rfc4122.

        @return: the generated guid
        @rtype: string
    """
    return "{%s}" % str(util.uuid1()).upper()


def generate_id():
    """
    Returns a random ID.
        
        @return: a random integer between 1000 and sys.maxint
        @rtype: integer
    """
    return random.randint(1000, sys.maxint)


class P2PMessage(gobject.GObject):
    """P2PMessage
    Abstracts and msnp2p message, and hides the need to manipulate
    a message as a set of chunks"""

    __gproperties__ = {
            "bytes-transferred" : (gobject.TYPE_UINT64,
                "Bytes transferred",
                "Number of bytes transferred so far.",
                consts.UINT64_MIN, consts.UINT64_MAX, 0,
                gobject.PARAM_READWRITE),

            "size" : (gobject.TYPE_UINT64,
                "Message size",
                "Message size in bytes.",
                consts.UINT64_MIN, consts.UINT64_MAX, 0,
                gobject.PARAM_READABLE),
    }

    def __init__(self, sender, recipient, id, flags, session_id, app_id, size,
                 content, acked_msg_id=generate_id(), prev_acked_msg_id=0,
                 acked_data_size=0):
        gobject.GObject.__init__(self)

        self.sender = sender
        self.recipient = recipient

        self.id = id
        self.flags = flags
        self.session_id = session_id
        self.app_id = app_id
        self.transferred = 0
        self.size = size
        self.content = content
        
        self.acked_msg_id = acked_msg_id
        self.prev_acked_msg_id = prev_acked_msg_id
        self.acked_data_size = acked_data_size

    def reset_content(self):
        if self.content != None:
            self.content.reset()

    def append_chunk(self, chunk):
        self.content.write(chunk)
        self.set_property("bytes-transferred", self.transferred + len(chunk))
        
    def extract_chunk(self, max_size):
        if self.content != None:
            chunk = self.content.read(max_size)
        else:
            chunk = ""

        self.set_property("bytes-transferred", self.transferred + len(chunk))

        return chunk

    def is_complete(self):
        return self.transferred == self.size

    def do_get_property(self, pspec):
        if pspec.name == "bytes-transferred":
            return self.transferred
        elif pspec.name == "size":
            return self.size
        else:
            raise AttributeError, "unknown property %s" % pspec.name

    def do_set_property(self, pspec, value):
        if pspec.name == "bytes-transferred":
            self.transferred = value
        else:
            raise AttributeError, "unknown property %s" % pspec.name

    def __str__(self):
        return "id=%d, flags=%#010x, session_id=%d, app_id=%d, size=%d" % \
            (self.id, self.flags, self.session_id, self.app_id, self.size)

class HttpStyleMessage(object):
    """Http style messages

    header1:value1\r\n
    header2:value2\r\n
    header3:value3\r\n
    \r\n
    body
    """
    def __init__(self):
        self.clear()
        
    def add_header(self, name, value):
        value = str(value)
        self.headers[name] = value
        self.seq_headers.append(name)

    def clear(self):
        self.headers = {}
        self.seq_headers = []
        self.body = ""
        
    def parse(self, chunk):
        HttpStyleMessage.clear(self)

        sections = chunk.split("\r\n\r\n", 1)

        if len(sections) > 1:
            self.body = sections[1]
        else:
            self.body = ""

        lines = sections[0].split("\r\n")
        for line_number, line in enumerate(lines):
            line = line.split(":", 1)
            name = line[0].strip()
            value = line[1].strip()
            self.add_header(name, value)

    def __str__(self):
        result = []
        for name in self.seq_headers:
            result.append(": ".join((name, self.headers[name])))
        result.append("")
        result.append(self.body)
        return "\r\n".join(result)


class SLPMessage(HttpStyleMessage):
    """ Abstraction of an MSNSLP message. """
    
    MESSAGE_TYPE_UNKNOWN  = 0
    MESSAGE_TYPE_REQUEST  = 1
    MESSAGE_TYPE_RESPONSE = 2

    STD_HEADERS = [ "To", "From", "Via", "CSeq", "Call-ID", "Max-Forwards" ]

    def __init__(self):
        HttpStyleMessage.__init__(self)
        self.clear()

    def clear(self):
        HttpStyleMessage.clear(self)
        self.method = ""
        self.status = -1
        
    def get_message_type(self):
        if self.method:
            return self.MESSAGE_TYPE_REQUEST
        elif self.status != -1:
            return self.MESSAGE_TYPE_RESPONSE
        else:
            return self.MESSAGE_TYPE_UNKNOWN

    def build_request(self, method, to="", frm="", branch="", command_sequence=0, call_id="", max_forwards=0):
        self.clear()
        self.method = method
        self.__build(to, frm, branch, command_sequence, call_id, max_forwards)

    def build_response(self, status, to="", frm="", branch="", command_sequence=0, call_id="", max_forwards=0):
        self.clear()
        self.status = status
        self.__build(to, frm, branch, command_sequence, call_id, max_forwards)
        
    def build_response_from_message(self, status, msg):
        self.clear()
        self.status = status

        # Copy all standard headers, incrementing CSeq if (when) we find it
        for name in msg.seq_headers:
            if name in self.STD_HEADERS:
                value = msg.headers[name][:]
                if name == "CSeq":
                    value = str(int(value) + 1)
                self.add_header(name, value)

        # Just swap these
        self.headers["To"] = msg.headers["From"][:]
        self.headers["From"] = msg.headers["To"][:]

    def add_body(self, body=None):
        """ Add MSNSLPBody object as body. """
        
        if body != None:
            content_type = body.content_type
            body_str = str(body)
            body_len = len(body_str)
        else:
            content_type = "null"
            body_str = ""
            body_len = 0

        self.add_header("Content-Type", content_type)
        self.add_header("Content-Length", body_len)
        self.body = body_str

    def parse(self, raw_message):
        if raw_message.find("MSNSLP/1.0") < 0:
            raise ParseError("message doesn't seem to be an MSNSLP/1.0 message")

        self.clear()
        start_line, content = raw_message.split("\r\n", 1)
        start_line = start_line.split(" ")

        if start_line[0] in ("INVITE", "BYE"):
            self.method = start_line[0].strip()
            self.status = -1
        else:
            self.method = ""
            self.status = int(start_line[1])

        HttpStyleMessage.parse(self, content)

    def __str__(self):
        result = []
        if self.method:
            result.append("%s MSNMSGR:%s MSNSLP/1.0" % (self.method, self._to))
        else:
            result.append("MSNSLP/1.0 %s" % status_message[self.status])
        result.append(HttpStyleMessage.__str__(self))
        return "\r\n".join(result)

    def __build(self, to, frm, branch, command_sequence, call_id, max_forwards):
        self._to = to

        if to:
            self.add_header("To", "<msnmsgr:%s>" % to)
        if frm:
            self.add_header("From", "<msnmsgr:%s>" % frm)
        if branch:
            self.add_header("Via", "MSNSLP/1.0/TLP ;branch=%s" % branch)
        self.add_header("CSeq", str(command_sequence))
        if call_id:
            self.add_header("Call-ID", call_id)
        self.add_header("Max-Forwards", str(max_forwards))


class SLPBody(HttpStyleMessage):
    def __init__(self, content_type):
        HttpStyleMessage.__init__(self)
        self.content_type = content_type

    def parse(self, data):
        HttpStyleMessage.parse(self, data)
        self.data = self.data[:-1] # remove the trailing \0

    def __str__(self):
        result = HttpStyleMessage.__str__(self)
        result += "\x00"
        return result


class SLPSessionInviteBody(SLPBody):
    def __init__(self):
        SLPBody.__init__(self, SLP_SESSION_REQ_CONTENT_TYPE)

    def build_request(self, euf_guid, session_id, s_chan_state, app_id, context, body=""):
        self.clear()
        self.add_header("EUF-GUID", euf_guid)
        self.add_header("SessionID", session_id)
        self.add_header("SChannelState", s_chan_state)
        self.add_header("AppID", app_id)
        self.add_header("Context", context)
        self.body = body

    def build_response(self, session_id, s_chan_state, body=""):
        self.clear()
        self.add_header("SessionID", session_id)
        self.add_header("SChannelState", s_chan_state)
        self.body = body

    def build_response_from_message(self, msg):
        self.clear()
        self.add_header("SessionID", msg.headers["SessionID"])
        self.add_header("SChannelState", msg.headers["SChannelState"])


class SLPSessionByeBody(SLPBody):
    def __init__(self):
        SLPBody.__init__(self, SLP_SESSION_CLOSE_CONTENT_TYPE)


class SLPTransferInviteBody(HttpStyleMessage):
    CONTENT_TYPE = "application/x-msnmsgr-transreqbody"

    def __init__(self):
        SLPBody.__init__(self, self.CONTENT_TYPE)

    def build(self, bridges, net_id, conn_type, upnpnat, icf,
              hashed_nonce, session_id, s_chan_state, data=""):
        self.clear()
        self.add_header("Bridges", bridges)
        self.add_header("NetID", net_id)
        self.add_header("Conn-Type", conn_type)
        self.add_header("UPnPNat", upnpnat)
        self.add_header("ICF", icf)
        self.add_header("Hashed-Nonce", hashed_nonce)
        self.add_header("SessionID", session_id)
        self.add_header("SChannelState", s_chan_state)
        self.data = data


class SLPDumbResponseRecipientError(SLPMessage):
    def __init__(self, bad_msg):
        SLPMessage.__init__(self)
        
        self.build_response_from_message(404, bad_msg)
        self.add_body()


class SLPDumbResponseContentError(SLPMessage):
    def __init__(self, bad_msg):
        SLPMessage.__init__(self)

        self.build_response_from_message(500, bad_msg)
        self.add_body()


class P2PTransport(gobject.GObject):
    """
    Base class for P2P transports.
    """

    __gsignals__ = {
            "p2p-peers-changed" : (gobject.SIGNAL_RUN_FIRST,
                                   gobject.TYPE_NONE,
                                   ()),
            "p2p-chunk-received" : (gobject.SIGNAL_RUN_FIRST,
                                    gobject.TYPE_NONE,
                                    (object, object,)),
            "p2p-chunk-sent" : (gobject.SIGNAL_RUN_FIRST,
                                gobject.TYPE_NONE,
                                (object, object,)),
    }

    def __init__(self, client):
        """Initializer
            
            @param client: an instance of Client.
            @type client: L{Client}"""
        gobject.GObject.__init__(self)
        client.p2p_transport_mgr._register_transport(self)

    def get_p2p_name(self):
        """ Returns the name of the transport.
            
            @return: the name of the transport.
            @rtype: string"""
        raise NotImplementedError

    def get_p2p_peers(self):
        """ Returns the peers on this transport (Contact objects).
            
            @return: peers on this transport
            @rtype: (L{protocol.Contact}, ...)"""
        raise NotImplementedError

    def get_p2p_rating(self):
        """ Returns the rating on a scale from 0 to 100.
            
            @return: the rating
            @rtype: integer"""
        raise NotImplementedError

    def get_p2p_max_chunk_size(self):
        """
        Get the maximum chunk size, which does not include the number of bytes
        required by the transports own framing.
            
            @return: chunk size
            @rtype: integer
        """
        raise NotImplementedError

    def send_p2p_chunk(self, peer, chunk, callback=None, cb_args=()):
        """ Send a raw P2P chunk.
            
            @param peer: recipient
            @type peer: protocol.Contact

            @param chunk: chunk to send
            @type chunk: string

            @param callback: callback to be use when the chunk has been transmitted
            @type callback: callable

            @param cb_args: callback arguments
            @type cb_args: tuple
            """
        raise NotImplementedError

class P2PTransportManager(gobject.GObject):
    """
    Manages P2PTransports and is responsible for sending P2PMessages
    using the most efficient P2PTransport.  P2PMessages might be sent
    chunked depending on their size and the selected P2PTransport's
    maximum transfer unit size. Each chunk is sent with the most
    efficient P2PTransport available at that point in time, so
    if a direct connection is established mid-transfer of a
    P2PMessage the chunks will be transferred over the direct
    connection.
    """

    __gsignals__ = {
            "receiving-message" : (gobject.SIGNAL_RUN_FIRST,
                                   gobject.TYPE_NONE,
                                   (object,)),
            "received-message" : (gobject.SIGNAL_RUN_FIRST,
                                  gobject.TYPE_NONE,
                                  (object,)),
            "receive-error" : (gobject.SIGNAL_RUN_FIRST,
                               gobject.TYPE_NONE,
                               (object,)),
            "sending-message" : (gobject.SIGNAL_RUN_FIRST,
                                 gobject.TYPE_NONE,
                                 (object,)),
            "sent-message" : (gobject.SIGNAL_RUN_FIRST,
                              gobject.TYPE_NONE,
                              (object,)),
            "send-error" : (gobject.SIGNAL_RUN_FIRST,
                            gobject.TYPE_NONE,
                            (object,)),
    }

    def __init__(self, client):
        """Initializer
            
            @param client: an instance of Client.
            @type client: L{Client}"""
        gobject.GObject.__init__(self)

        self.client = client

        self._transports = []

        self.__incoming = {}
        self.__outgoing = {}
        self.__sent = {}

        self.__calculate_best_transports()

    def __calculate_best_transports(self):
        """
        Internal method used to update the mappings of contacts to the
        best currently available transport.
        """
        self.__best_transports = {}
        for transport, handlers in self._transports:
            rating = transport.get_p2p_rating()
            for peer in transport.get_p2p_peers():
                if peer in self.__best_transports:
                    prev_rating = self.__best_transports[peer].get_p2p_rating()
                    if rating > prev_rating:
                        self.__best_transports[peer] = transport
                else:
                    self.__best_transports[peer] = transport

    def _register_transport(self, transport):
        """ Called implicitly by P2PTransport's constructor. """
        handlers = []
        connect = transport.connect
        handlers.append(connect("p2p-peers-changed", lambda *args: self.__calculate_best_transports()))
        handlers.append(connect("p2p-chunk-received", self.__on_chunk_received))
        self._transports.append((transport, handlers))
        self.__calculate_best_transports()

    def _unregister_transport(self, transport):
        """ Called by P2PTransport when the transport goes down. """
        for i, cur_transport, handlers in enumerate(self.transports):
            if cur_transport == transport:
                for id in handlers:
                    transport.handler_disconnect(id)
                del self.transports[i]
                self.__calculate_best_transports()
                return

    def _find_best_transport(self, peer):
        """ Find the best transport for a given peer. """
        if peer in self.__best_transports:
            return self.__best_transports[peer]
        else:
            return self.client._get_default_p2p_transport(peer)

    def __on_chunk_received(self, transport, sender, chunk):
        """ Handler called when a transport receives a chunk. """
        # Unpack header
        header = struct.unpack("<LLQQLLLLQ", chunk[:48])
        
        # Just pretend that AppID is part of the header... ;-)
        header = list(header)
        header.append(struct.unpack(">L", chunk[-4:])[0])
        
        # Is it an acknowledgement?
        if header[P2P_FLAGS] & P2P_FLAGS_ACK != 0:
            acked_id = header[P2P_ACKED_MSG_ID]
            if acked_id in self.__sent:
                msg = self.__sent[acked_id]
                del self.__sent[acked_id]
                msg.reset_content()
                self.emit("sent-message", msg)
            else:
                logger.error("got acknowledgement for an unknown message")

            return

        # Extract the body
        body_size = header[P2P_CHUNK_SIZE]
        body = chunk[48:48 + body_size]

        # Are we dealing with a new message?
        id = header[P2P_MESSAGE_ID]
        if not id in self.__incoming:
            content = self.client.slp_call_factory._create_message_content(header)

            msg = P2PMessage(sender, None,
                             header[P2P_MESSAGE_ID],
                             header[P2P_FLAGS],
                             header[P2P_SESSION_ID],
                             header[P2P_APP_ID],
                             header[P2P_DATA_SIZE],
                             content)

            self.__incoming[id] = msg

            self.emit("receiving-message", msg)
        else:
            msg = self.__incoming[id]
        
        # Check that offset matches the number of bytes transferred so far
        if header[P2P_DATA_OFFSET] != msg.transferred:
            logger.error("message offset %u doesn't match the number of bytes transferred so far (%u)" % \
                         (header[P2P_DATA_OFFSET], msg.transferred))
            self.emit("receive-error", msg)
            del self.__incoming[id]
            return

        # Add the new chunk
        msg.append_chunk(body)
        self.emit("receiving-message", msg)

        # Is the message fully received?
        if msg.is_complete():
            logger.debug("Received p2p message of size %d" % msg.size)
            self.__acknowledge_message(header, msg)

            msg.reset_content()
            self.emit("received-message", msg)
            del self.__incoming[id]

    def __acknowledge_message(self, header, msg):
        """ Internal helper method for acknowledging a message. """
        ack_msg = P2PMessage(None, msg.sender,
                             generate_id(), P2P_FLAGS_ACK, msg.session_id,
                             msg.app_id, 0, None, header[P2P_MESSAGE_ID],
                             header[P2P_ACKED_MSG_ID], msg.size)
        self.send_message(ack_msg)

    def send_message(self, msg):
        """Send a P2PMessage.
            
            @param msg: the message to send
            @type msg: L{P2PMessage}"""
        self.__outgoing[msg.id] = msg
        self.emit("sending-message", msg)
        self.__send_next_chunk(msg)

    def __send_next_chunk(self, msg):
        """
        Internal helper method to send the next chunk of a P2P message.
        """

        transport = self._find_best_transport(msg.recipient)

        max_body_size = transport.get_p2p_max_chunk_size() - 48 - 4
        body = msg.extract_chunk(max_body_size)
        
        header = struct.pack("<LLQQLLLLQ",
                             msg.session_id,
                             msg.id,
                             msg.transferred - len(body),
                             msg.size,
                             len(body),
                             msg.flags,
                             msg.acked_msg_id,
                             msg.prev_acked_msg_id,
                             msg.acked_data_size)

        footer = struct.pack(">L", msg.app_id)

        if msg.is_complete:
            del self.__outgoing[msg.id]

            if msg.flags & P2P_FLAGS_ACK == 0:
                self.__sent[msg.id] = msg

            callback = None
            cb_args = ()
        else:
            callback = self.__send_next_chunk
            cb_args = (msg,)

        chunk = header + body + footer
        transport.send_p2p_chunk(msg.recipient, chunk, callback, cb_args)

        self.emit("sending-message", msg)


class SLPCallFactory:
    CALL_HANDLERS = {}

    def __init__(self, client):
        """Initializer
            
            @param client: an instance of Client.
            @type client: L{Client}"""
        self.client = client

        client.p2p_transport_mgr.connect("received-message",
                                         self.__on_message_received)

        self.cid_to_call = {}
        self.sid_to_call = {}
        
        self.CALL_HANDLERS[EUF_GUID_MSNOBJECT] = { 11 : EmoticonCall,
                                                   12 : DisplayPictureCall }

    def _register_call(self, call):
        self.cid_to_call[call.call_id] = call
        self.sid_to_call[call.session_id] = call

    def _unregister_call(self, call):
        del self.cid_to_call[call.call_id]
        del self.sid_to_call[call.session_id]

    def _create_message_content(self, header):
        """
        Create the message content file object.  Called by TransportManager
        when a new message is about to be received.
        """

        sid = header[P2P_SESSION_ID]
        if sid != 0 and sid in self.sid_to_call:
            content = self.sid_to_call[sid]._create_message_content(header)
        else:
            content = StringIO.StringIO()

        return content

    def __on_message_received(self, transport_mgr, message):
        if message.app_id == 0:
            raw_msg = message.content.read()
            
            if len(raw_msg) == 0:
                logger.warning("got an empty SLP message: '%s'" % message)
                return

            slp_msg = SLPMessage()
            slp_msg.parse(raw_msg)

            cid = slp_msg.headers["Call-ID"]
            if not cid in self.cid_to_call:
                if slp_msg.get_message_type() != slp_msg.MESSAGE_TYPE_REQUEST:
                    raise ProtocolError("Message from unknown call ID is not a request")

                if slp_msg.method != "INVITE":
                    raise ProtocolError("Message from unknown call ID has method %s, expected INVITE" % slp_msg.method)

                self.__create_call_from_invite(message.sender, slp_msg)
            else:
                call = self.cid_to_call[cid]
                call._dispatch_slp_message(message.sender, slp_msg)
        else:
            sid = message.session_id
            if sid == 0:
                raise ProtocolError("Message with nonzero AppID but sid=0")

            if not sid in self.sid_to_call:
                raise ProtocolError("Message with unknown sid=%d" % sid)

            call = self.sid_to_call[sid]
            call._dispatch_app_message(message)

    def __create_call_from_invite(self, sender, slp_msg):
        slp_body = HttpStyleMessage()
        slp_body.parse(slp_msg.body)
        
        type = UnknownCall
        
        euf = slp_body.headers["EUF-GUID"]
        if euf in self.CALL_HANDLERS:
            entry = self.CALL_HANDLERS[euf]
            
            app_id = slp_body.headers["AppID"]
            if app_id in entry:
                type = entry[app_id]

        call = type(self.client)
        call._dispatch_slp_message(sender, slp_msg)


class SLPCall(gobject.GObject):
    """
    An abstract SLP call.
    """
    
    def __init__(self, client, euf_guid="", app_id=-1):
        """Initializer
            
            @param client: an instance of Client.
            @type client: L{Client}
            """
        #TODO: document euf_guid and app_id
        gobject.GObject.__init__(self)
        
        self.client = client
        self.factory = client.slp_call_factory
        self.profile = client.profile

        self.euf_guid = euf_guid
        self.app_id = app_id

        # set a clean state
        self.__initialized = False

        self.peer = ""
        self.call_id = ""

        self.session_id = None

        # Requests awaiting response, in- and outbound
        self.__pending_in = {}
        self.__pending_out = {}

    ### Factory API
    def _create_message_content(self, header):
        return StringIO.StringIO()

    def _dispatch_slp_message(self, sender, message):
        try:
            # Dumb checks (before we store any state)
            try:
                frm = message.headers["From"]
                to = message.headers["To"]
                call_id = message.headers["Call-ID"]
                content_type = message.headers["Content-Type"]
                via = message.headers["Via"]
                seqid = int(message.headers["CSeq"])
            except KeyError, e:
                raise SLPError(SLPDumbResponseContentError(message))
            except ValueError, e:
                raise SLPError(SLPDumbResponseContentError(message))

            try:
                self.__check_from_to_field(frm, sender.get_property("passport"))
            except ParseError, e:
                raise ProtocolError("From field doesn't match sender, ignoring possible spoof attempt: '%s'" % e)

            try:
                branch_id = self.__extract_branch(via)
            except ParseError, e:
                logger.error("failed to extract branch: '%s'" % e)
                raise SLPError(SLPDumbResponseContentError(message))

            try:
                self.__check_from_to_field(to, self.profile.get_property("passport"))
            except ParseError, e:
                raise SLPError(SLPDumbResponseRecipientError(message))

            body = HttpStyleMessage()
            body.parse(message.body)

            msg_type = message.get_message_type()

            # Are we initialized?
            if not self.__initialized:
                if msg_type != message.MESSAGE_TYPE_REQUEST:
                    raise ProtocolError("request before initialization")
                self._initialize(sender, call_id)

            # Okay, we're good to go
            if msg_type == message.MESSAGE_TYPE_REQUEST:
                self.__pending_in[branch_id] = (seqid, message, body)

                self.__dispatch_slp_request(branch_id, message, content_type, body)
            elif msg_type == message.MESSAGE_TYPE_RESPONSE:
                if not branch_id in self.__pending_out:
                    raise ProtocolError("response for a request we don't know about")

                callback, args = self.__pending_out[branch_id]
                del self.__pending_out[branch_id]

                if callback:
                    callback(message, body, *args)
            else:
                raise SLPError(SLPDumbResponseContentError(message))
        except SLPError, e:
            logger.warning("SLP error occured: '%s', responding with error message with status=%d", (e, e.response_msg.status))
            self._send_slp_message(e.response_msg, sender)
        except ProtocolError, e:
            logger.warning("Protocol error occured while dispatching SLP message: '%s'" % e)

    def __dispatch_slp_request(self, id, msg, content_type, body):
        if msg.method == "INVITE":
            if content_type == SLP_SESSION_REQ_CONTENT_TYPE:
                if not "Context" in body.headers:
                    self._send_session_unk_error(id)
                    return

                self._on_session_invite(id, msg, body)            
            elif content_type == SLP_TRANSFER_REQ_CONTENT_TYPE:
                self.__on_transfer_request(id, msg, body)
            else:
                logger.warning("ignoring INVITE request with unknown content type: '%s'" % content_type)
        elif msg.method == "BYE":
            if content_type == SLP_SESSION_CLOSE_CONTENT_TYPE:
                self._on_session_bye(id, msg, body)            
            else:
                logger.warning("ignoring BYE request with unknown content type: '%s'" % content_type)
        else:
            # Shouldn't ever happen
            logger.warning("ignoring request with unknown method '%s'" % msg.method)

    def __on_transfer_request(self, id, msg, body):
        logger.debug("__on_transfer_request")

        # FIXME: for now we just decline these
        self._send_slp_response(id, 603, None)

    def _dispatch_app_message(self, message):
        self._on_app_message_received(message)

    ### Internal convenience
    def __check_from_to_field(self, field, expected):
        if field[0] != "<" or field[-1] != ">":
            raise ParseError("not surrounded by brackets")
        field = field[1:-1]
        tokens = field.split(":", 1)
        if len(tokens) != 2:
            raise ParseError("no colon found")
        if tokens[0] != "msnmsgr":
            raise ParseError("transport is not msnmsgr")
        if tokens[1] != expected:
            raise ParseError("recipient is '%s', expected '%s'" % (tokens[1], expected))

    def __extract_branch(self, field):
        tokens = field.split(";", 1)
        if len(tokens) != 2:
            raise ParseError("no semicolon found")
        guid = tokens[1].strip()[7:]
        return guid

    ### Internal API
    def _initialize(self, peer,
                    call_id=generate_guid(),
                    session_id=generate_id()):
        assert not self.__initialized
        self.__initialized = True

        self.peer = peer
        self.call_id = call_id
        self.session_id = session_id

        self.factory._register_call(self)

    def _uninitialize(self):
        if not self.__initialized:
            return
        self.factory._unregister_call(self)

    def _close(self, send_bye):
        if send_bye:
            self._send_session_bye()
        self._uninitialize()

    def _send_message(self, flags, app_id, content=None, size=0, recipient=None):
        if recipient == None:
            recipient = self.peer

        if app_id != 0:
            sid = self.session_id
        else:
            sid = 0

        msg = P2PMessage(None, recipient, generate_id(), flags,
                         sid, app_id, size, content)

        self.client.p2p_transport_mgr.send_message(msg)

    def _send_slp_message(self, slp_msg, recipient=None):
        content_str = str(slp_msg)
        content = StringIO.StringIO(content_str)
        self._send_message(P2P_FLAGS_NONE, 0, content, len(content_str), recipient)

    def _send_slp_request(self, type, body, callback=None, cb_args=(), response_expected=True):
        branch_id = generate_guid()
        if response_expected:
            self.__pending_out[branch_id] = (callback, cb_args)

        msg = SLPMessage()
        msg.build_request(type, self.peer.get_property("passport"),
                          self.profile.get_property("passport"),
                          branch_id, 0, self.call_id)
        msg.add_body(body)

        self._send_slp_message(msg)

    def _send_slp_response(self, id, status, body):
        seqid = self.__pending_in[id][0]
        del self.__pending_in[id]

        msg = SLPMessage()
        msg.build_response(status, self.peer.get_property("passport"),
                           self.profile.get_property("passport"),
                           id, seqid + 1, self.call_id)
        msg.add_body(body)

        self._send_slp_message(msg)

    def _send_session_invite(self, context, callback=None, cb_args=()):
        body = SLPSessionInviteBody()
        body.build_request(self.euf_guid, self.session_id, 0, self.app_id, context)

        self._send_slp_request("INVITE", body, callback, cb_args)

    def _send_session_response(self, id, status):
        body = SLPSessionInviteBody()
        body.build_response(self.session_id, 0)

        self._send_slp_response(status, body)

    _send_session_accept = lambda self, id: self._send_session_response(id, 200)
    _send_session_reject = lambda self, id: self._send_session_response(id, 603)
    _send_session_unk_error = lambda self, id: self._send_session_response(id, 500)
    _send_session_not_found = lambda self, id: self._send_session_response(id, 404)

    def _send_session_bye(self):
        body = SLPSessionByeBody()
        self._send_slp_request("BYE", body, response_expected=False)

    def _send_app_message(self, flags, content, size):
        self._send_message(flags, self.app_id, content, size)
        
    def _send_app_message_from_string(self, flags, data):
        content = StringIO.StringIO(data)
        self._send_app_message(flags, content, len(data))

    ### Callbacks meant to be overridden
    def _on_session_invite(self, id, msg, body):
        logger.debug("_on_session_invite")

    def _on_session_bye(self, id, msg, body):
        logger.debug("_on_session_bye")

    def _on_app_message_received(self, msg):
        logger.debug("_on_app_message_received")


class UnknownCall(SLPCall):
    def _on_session_request(self, id, msg, body):
        logger.warning("got invite for unknown call type, rejecting")
        self._send_session_unk_error(id)


class MSNObjectCall(SLPCall):
    def __init__(self, client, app_id):
        SLPCall.__init__(self, client, EUF_GUID_MSNOBJECT, app_id)
        self._obj_received_cb = None
        self.__app_msg_count = 0

    def _request_msn_object(self, contact, msn_object, callback):
        assert self._obj_received_cb == None
        
        self._obj_received_cb = callback

        context = standard_b64encode(msn_object)
        self._initialize(contact)
        self._send_session_invite(context, self.__on_session_invite_response)

    def __emit_result(self, result):
        cb = self._obj_received_cb
        self._obj_received_cb = None
        cb(result)

    def __on_session_invite_response(self, msg, body):
        if msg.status != 200:
            self.__emit_result(None)
            self._close(False)
            return
        
        logger.debug("%s: got session accept" % self.__class__.__name__)

    def _on_app_message_received(self, msg):
        cls_name = self.__class__.__name__

        if self.__app_msg_count == 0:
            logger.debug("%s: received data preparation message" % cls_name)
        elif self.__app_msg_count == 1:
            logger.debug("%s: received DP message" % cls_name)

            self.__emit_result(msg.content.read())
            self._close(True)
        else:
            logger.debug("%s: received unexpected message" % cls_name)

        self.__app_msg_count += 1

    def _on_session_invite(self, id, msg, body):
        ctx = body.headers["Context"]
        msn_object = standard_b64decode(ctx)
        
        file, size = self._get_local_msn_object(msn_object)
        if file == None:
            self._send_session_not_found(id)
            return

        self._send_session_accept(id)
        self._send_app_message_from_string(P2P_FLAGS_NONE, "\x00\x00\x00\x00")
        self._send_app_message(P2P_FLAGS_DATA, file, size)

    def _get_local_msn_object(self, msn_object):
        # FIXME: implement this
        return (None, 0)

    def _on_session_bye(self, id, msg, body):
        self._close(False)


class EmoticonCall(MSNObjectCall):
    APP_ID = 11

    def __init__(self, client):
        MSNObjectCall.__init__(self, client, self.APP_ID)

    def request(self, contact, msn_object, callback):
        self._request_msn_object(contact, msn_object, callback)


class DisplayPictureCall(MSNObjectCall):
    APP_ID = 12

    def __init__(self, client):
        MSNObjectCall.__init__(self, client, self.APP_ID)

    def request(self, contact, callback):
        msnobj = contact.get_property("msnobject")
        logger.debug("msnobject: '%s'" % msnobj)
        if msnobj == "":
            raise ValueError("no msnobject known")

        self._request_msn_object(contact, msnobj, callback)
