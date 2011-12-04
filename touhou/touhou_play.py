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

from graphics.animated import Animated
from graphics.graphic import GraphicAbsPositioned
import misc.astar as astar

from touhou_level import TouhouLevel, TouhouCreature
from touhou_ui import TouhouUI
from gfx_manager import GfxManager
from touhou_names import *
from touhou_menu import Menu
from touhou_ui_manager import UI

E_UPDATE_SPRITE_FRAMES = USEREVENT+1
E_UPDATE_SPRITE_POSITIONS = USEREVENT+2
E_USER_INPUT = USEREVENT+3
E_OBJECT_SIGNAL = USEREVENT+4

class TouhouPlay:
    SCROLL_SPEED = 5
    def __init__(self, level_state):
        self.level = level_state
        self.level.map.load_graphics()

        self.map = self.level.map
        self.gfx_manager = GfxManager()

        pygame.time.set_timer(E_UPDATE_SPRITE_FRAMES,200)
        pygame.time.set_timer(E_UPDATE_SPRITE_POSITIONS,50)

        self.ui = TouhouUI(self.level)
        self.ui.generate_menus()

        self.event_catalog = {}
        self.assign_event_handler(QUIT, self.quit)

        self.assign_event_handler(E_UPDATE_SPRITE_FRAMES,self.map.frame_update) # For animated sprites
        self.assign_event_handler(E_UPDATE_SPRITE_POSITIONS,self.map.update_objects) # Movement
        self.assign_event_handler(E_USER_INPUT,self.ui_events)
        self.assign_event_handler(E_OBJECT_SIGNAL,self.object_events)
        self.assign_event_handler(KEYDOWN, self.ui.key_down)
        self.assign_event_handler(KEYUP, self.ui.key_up)
        self.assign_event_handler(MOUSEBUTTONDOWN, self.ui.update_mouse)
        self.assign_event_handler(MOUSEBUTTONUP, self.ui.update_mouse)
        self.assign_event_handler(MOUSEMOTION, self.ui.update_mouse)

    def start(self):
        self.running = True

    def quit(self, e):
        self.running = False

        # Assign a function to the event. Can't be overwritten.
    # e: event name, handler: function name
    def assign_event_handler(self, event_type, handler):
        if event_type not in self.event_catalog:
            self.event_catalog[event_type] = handler
        else:
            raise OverwriteError(event_type, self.event_catalog[event_type])

    def process(self, event_list):
        self.ui.update((self.gfx_manager.x,self.gfx_manager.y))
        self.process_ui()
        self.gfx_manager.register_draw(self.map.draw_ground())
        self.gfx_manager.register_draw(self.ui.ui.draw_under())
        self.gfx_manager.register_draw(self.map.draw_sprites())
        self.gfx_manager.register_draw(self.ui.ui.draw())
        
        for e in event_list:
            try:
                f = self.event_catalog[e.type]
                f(e)
            except KeyError:
                pass
                #print e, "event not registered"
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
        elif data.mode == I_ATTACK:
            pass
        else:
            print "Unexpected Mode"

    def _attack(self, attacker, defender):
        damage = self.level.creatures[attacker].attack
        self.level.creatures[defender].change_hp(-damage)
        print attacker, "attacks", defender, "for", damage
        print defender, "has", self.level.creatures[defender].hp, "hp"
        if self.level.creatures[defender].hp <= 0:
            print defender, "died."
            self.level.kill_creature(defender)
            self.ui.unselect()

    def ui_events(self, e):
        ui_command = e.subtype
        if ui_command == MOVETO:
            self.move_character(e)
        elif ui_command == ENDTURN:
            self.level.end_turn()
        elif ui_command == ATTACK:
            try:
                attacker = e.attacker
                defender = self.level.get_object(e.target)
                self.ui.set_selected_object(e.target)
                self._attack(attacker, defender)
            except:
                print "Invalid Attack Command"

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
        if self.ui.keybuffer[K_UP]:
            self.gfx_manager.shift((0,-self.SCROLL_SPEED))
        elif self.ui.keybuffer[K_DOWN]:
            self.gfx_manager.shift((0,self.SCROLL_SPEED))
        if self.ui.keybuffer[K_LEFT]:
            self.gfx_manager.shift((self.SCROLL_SPEED,0))
        elif self.ui.keybuffer[K_RIGHT]:
            self.gfx_manager.shift((-self.SCROLL_SPEED,0))

class OverwriteError(Exception):
    def __init__(self, signal, handler):
        self.signal = signal
        self.handler = handler

    def __str__(self):
        print "Event ", self.signal, "already assigned to ", self.handler, "."
