# -*- coding: utf-8 -*-
#
# Copyright (C) 2007  Ali Sabil <ali.sabil@gmail.com>
# Copyright (C) 2007  Ole André Vadla Ravnås <oleavr@gmail.com>
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

__all__ = ["BaseEventInterface"]

class BaseEventInterface(object):
    def __init__(self, client):
        self._client = client
        self._client.register_events_handler(self)

    def _dispatch_event(self, event_name, *params):
        try:
            handler = getattr(self, event_name)
        except Exception, e:
            return

        handler(*params)
