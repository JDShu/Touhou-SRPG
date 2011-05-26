'''
* This file is part of Touhou SRPG.
* Copyright (c) Hans Lo
*
* Touhou SRPG is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* Touhou SRPG is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with Touhou SRPG.  If not, see <http://www.gnu.org/licenses/>.
'''

from pygame.locals import *

# Core class that does basic event handling.
class Session:
    def __init__(self):

        self.event_catalog = {}
        self.running = False

        self.register_event(QUIT, self.quit)

    def start(self):
        self.running = True

    # Assign a function to the event. Can't be overwritten.
    # e: event name, handler: function name
    def register_event(self, e_type, handler):
        if e_type not in self.event_catalog:
            self.event_catalog[e_type] = handler
        else:
            raise OverwriteError(e_type, self.event_catalog[e_type])

    # Process everything!
    def process(self, event_list):
        for e in event_list:
            try:
                f = self.event_catalog[e.type]
                f(e)
            except KeyError:
                pass
                #print e, "event not registered"

    def draw(self):
        print "draw() not implemented"

    def quit(self, e):
        self.running = False

class OverwriteError(Exception):
    def __init__(self, signal, handler):
        self.signal = signal
        self.handler = handler

    def __str__(self):
        print "Event ", self.signal, "already assigned to ", self.handler, "."
