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
from pygame.locals import *

from core.input_session import IOSession
from core.ui import UI
from core.graphics.animated import Animated
from core.misc import astar

from touhou_level import TouhouLevel
from touhou_ui import TouhouUI

class TouhouPlay(IOSession):
    SCROLL_SPEED = 5
    def __init__(self, level_state):
        IOSession.__init__(self)
        self.level_state = level_state
        self.map = self.level_state.map
        self.ui = TouhouUI(self.map)

        #test code
        self.test_reimu = Animated("reimu")
        self.map.place_object(self.test_reimu, (6,1))
        self.map.grid[6][1].move_path([(7,1),(7,2),(7,3)])

        pygame.time.set_timer(USEREVENT+1,200)
        pygame.time.set_timer(USEREVENT+2,100)
        self.register_event(USEREVENT+1,self.test_reimu.update)
        
        self.register_event(USEREVENT+2,self.map.update)
        

    def process(self, event_list):
        #self.test_reimu.update()
        self.ui.update(self.mouse_coords, self.mouse_state, self.keybuffer,(self.x,self.y))
        self.register_draw(self.map.draw())
        self.register_draw(self.ui.draw())
        IOSession.process(self, event_list)
        self.scroll_map()

    #helper isometric movement function
    def move_object_single(self):
        pass

    def scroll_map(self):
        if self.keybuffer[K_UP]:
            self.shift((0,-self.SCROLL_SPEED))
        elif self.keybuffer[K_DOWN]:
            self.shift((0,self.SCROLL_SPEED))
        if self.keybuffer[K_LEFT]:
            self.shift((self.SCROLL_SPEED,0))
        elif self.keybuffer[K_RIGHT]:
            self.shift((-self.SCROLL_SPEED,0))
