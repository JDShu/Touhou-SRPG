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
from core.ui import UI, Menu
from core.graphics.animated import Animated
from core.graphics.graphic import GraphicAbsPositioned
from core.misc import astar

from touhou_level import TouhouLevel
from touhou_ui import TouhouUI
from touhou_graphic import Character

class TouhouPlay(IOSession):
    SCROLL_SPEED = 5
    def __init__(self, level_state):
        IOSession.__init__(self)
        self.level_state = level_state
        self.map = self.level_state.map
        self.ui = TouhouUI(self.map)

        #test code
        test_reimu = Animated("reimu")
        reimu_info = Character("reimu",5)
        self.map.place_object(test_reimu, (6,1), reimu_info)
        p = [(6,2),(6,3),(7,3)]
        self.map.grid[6][1].move_path(p)

        #sample character menu
        reimu_menu = Menu("Reimu")
        reimu_menu.set_body_graphic("./content/gfx/gui/menu_body.png")
        reimu_menu.set_entry_hover_graphic("./content/gfx/gui/menu_option.png")
        reimu_menu.set_w(80)
        reimu_menu.set_header_height(30)
        reimu_menu.set_entry_height(30)
        reimu_menu.add_entry("Move", self.ui.option_move)
        reimu_menu_placed = GraphicAbsPositioned(reimu_menu,(0,0))
        self.ui.add_menu(reimu_info, reimu_menu_placed)

        #self.map.grid[6][1].move_path([(7,1),(7,2),(7,3)])

        pygame.time.set_timer(USEREVENT+1,200)
        pygame.time.set_timer(USEREVENT+2,100)
        self.register_event(USEREVENT+1,test_reimu.update)
        
        self.register_event(USEREVENT+2,self.map.update)
        
    # get
    #def move_character
    
    def process(self, event_list):
        #self.test_reimu.update()
        self.ui.update(self.mouse_coords, self.mouse_state, self.keybuffer,(self.x,self.y))
        self.process_ui()
        self.register_draw(self.map.draw())
        self.register_draw(self.ui.draw())
        IOSession.process(self, event_list)
        self.scroll_map()

    # Respond to changes in UI interface
    def process_ui(self):
        #info = self.ui.data
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
