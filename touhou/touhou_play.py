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

from core.input_session import IOSession
from core.ui import UI

from touhou_level import TouhouLevel

class TouhouPlay(IOSession):
    SCROLL_SPEED = 3
    def __init__(self, level_state):
        IOSession.__init__(self)
        self.level_state = level_state
        self.map = self.level_state.map
        self.ui = UI()

    def process(self, event_list):
        self.register_draw(self.map.draw())
        self.register_draw(self.ui.draw())
        IOSession.process(self, event_list)
        self.scroll_map()

    def scroll_map(self):
        if self.keybuffer[K_UP]:
            self.shift((0,-self.SCROLL_SPEED))
        elif self.keybuffer[K_DOWN]:
            self.shift((0,self.SCROLL_SPEED))
        if self.keybuffer[K_LEFT]:
            self.shift((self.SCROLL_SPEED,0))
        elif self.keybuffer[K_RIGHT]:
            self.shift((-self.SCROLL_SPEED,0))
