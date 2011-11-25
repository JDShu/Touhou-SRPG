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
import pickle
from pygame.locals import *

from core.input_session import IOSession
from core.ui import UI, Menu
from core.graphics.animated import Animated
from core.graphics.graphic import GraphicAbsPositioned
import core.misc.astar as astar

from touhou_level import TouhouLevel, TouhouCreature
from touhou_ui import TouhouUI
from touhou_names import *

class TouhouPlay(IOSession):
    SCROLL_SPEED = 5
    def __init__(self, level_state):
        IOSession.__init__(self)
        f = open("./content/level/test.lvl", "r")
        self.level = pickle.load(f)
        self.level.map.load_graphics()

        self.map = self.level.map
        self.ui = TouhouUI(self.level)
        self.ui.generate_menus()

        pygame.time.set_timer(USEREVENT+1,200)
        pygame.time.set_timer(USEREVENT+2,50)

        self.register_event(USEREVENT+1,self.map.frame_update) # For animated sprites
        self.register_event(USEREVENT+2,self.map.update_objects) # Movement
        self.register_event(USEREVENT+3,self.ui_events)
        self.register_event(USEREVENT+4,self.object_events)

    def process(self, event_list):
        #self.test_reimu.update()
        self.ui.update(self.mouse_coords, self.mouse_state, self.keybuffer,(self.x,self.y))
        self.process_ui()
        self.register_draw(self.map.draw_ground())
        self.register_draw(self.ui.ui.draw_under())
        self.register_draw(self.map.draw_sprites())
        self.register_draw(self.ui.ui.draw())
        IOSession.process(self, event_list)
        self.scroll_map()

    # Respond to changes in UI interface
    def process_ui(self):
        data = self.ui.data
        if data.mode == I_BROWSE:
            pass
        elif data.mode == I_MOVE:
            if data.dest:
                path = astar.path(self.map, data.selected.pos, data.dest)
                x,y = self.ui.data.selected.pos
                self.map.grid[x][y].move_path(path)

    def ui_events(self, e):
        if e.subtype == MOVETO:
            self.move_character(e)
        elif e.subtype == ENDTURN:
            self.level.end_turn()
        elif e.subtype == ATTACK:
            damage = self.level.creatures[e.attacker].attack
            target = self.level.get_object(e.target)
            self.level.creatures[target].change_hp(-damage)
            print e.attacker, "attacks", target, "for", damage
            print target, "has", self.level.creatures[target].hp, "hp"
            self.ui.set_selected_object(e.target)
            if self.level.creatures[target].hp <= 0:
                print target, "died."
                self.level.kill_creature(target)
                self.ui.unselect()

    def object_events(self, e):
        if e.subtype == OBJECTEVENT:
            self.map.update_obj_pos(e.obj)
            if not e.obj.moving:
                self.ui.set_browse()

    def move_character(self, e):
        pos = self.map.obj_list[e.name]
        path = astar.path(self.map, pos, e.dest)
        x,y = pos
        self.map.grid[x][y].move_path(path)

    def scroll_map(self):
        if self.keybuffer[K_UP]:
            self.shift((0,-self.SCROLL_SPEED))
        elif self.keybuffer[K_DOWN]:
            self.shift((0,self.SCROLL_SPEED))
        if self.keybuffer[K_LEFT]:
            self.shift((self.SCROLL_SPEED,0))
        elif self.keybuffer[K_RIGHT]:
            self.shift((-self.SCROLL_SPEED,0))
