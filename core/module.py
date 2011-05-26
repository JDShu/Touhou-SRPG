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

import pygame

# Base class for SRPG modules.
class Module:
    def __init__(self):
        self.session = None
        self.session_list = {}
        
    def start_session(self):
        self.session.start()

    def load_session(self, s_name):
        self.session = self.session_list[s_name]

    def process(self):
        events = pygame.event.get()
        self.session.process(events)

    def draw(self):
        self.session.draw()

    def register_session(self,s_name, session):
        self.session_list[s_name] = session

    def session_running(self):
        return self.session.running
