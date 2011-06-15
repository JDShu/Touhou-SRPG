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

from OpenGL.GL import *

import pygame
from pygame.locals import *
from math import *

from core.graphics.graphic import Graphic, GraphicPositioned, GraphicAbsPositioned
from core.ui import UI, Menu

from touhou_graphic import MapGraphic, Highlight

#Interface modes
I_BROWSE, I_MOVE, I_ATTACK = range(3)

# UI Event subtypes
MOVETO, ATTACK, ENDTURN = range(3)

UI_EVENT = USEREVENT+3

class TouhouUI(UI):
    
    def __init__(self, level):

        self.level = level
        self.map = level.map

        self.map_w, self.map_h = self.map.w, self.map.h
        # Constants we need to calculate mouse position and hovering highlight
        self.off_x, self.off_y = self.map.TILE_OFFSET[0], self.map.TILE_OFFSET[1]
        self.off_x = float(self.off_x)
        self.off_y = float(self.off_y)
        self.theta_x = atan(self.off_x/self.off_y)
        self.theta_y = atan(self.off_y/self.off_x)
        self.hyp = hypot(self.off_x-3, self.off_y-3) #dirty adjustment for select highlight precision
        self.max_x, self.max_y = self.map_w*self.hyp, self.map_h*self.hyp
       
        self.menus = {}
        self.data = UIData()

        UI.__init__(self)
        self.left, self.middle, self.right = (0,0,0)

        #Test code - sample menu and hovering tile
        self.main_menu = Menu("Main")
        self.main_menu.set_body_graphic("./content/gfx/gui/menu_body.png")
        self.main_menu.set_entry_hover_graphic("./content/gfx/gui/menu_option.png")
        self.main_menu.set_w(80)
        self.main_menu.set_header_height(30)
        self.main_menu.set_entry_height(30)
        self.main_menu.add_entry("Quit", self.option_quit)
        self.main_menu.add_entry("End Turn", self.end_turn)
        self.main_menu_placed = GraphicAbsPositioned(self.main_menu,(0,0))

        hover_graphic = Graphic("./content/gfx/sprites/hover.png", 0.5)
        
        self.hover_tile = MapGraphic(hover_graphic, (0,0), "hover")
        self.highlight = Highlight(hover_graphic)
                
        self.add(self.main_menu_placed)
        self.status_window = StatusWindow()
        self.status_window = GraphicAbsPositioned(self.status_window, (0,0))
        self.status_window.make_visible()
        self.add(self.status_window)
        self.add_under(self.hover_tile)
        self.add_under(self.highlight)

        #One menu showing at any time
        self.current_menu = None

        #self.data.mode = BROWSE

    def end_turn(self):
        pygame.event.post(End_Turn_Event())

    def set_mode(self, mode):
        self.data.mode = mode

    # Attach a name to a menu and add to ui list.
    def add_menu(self, obj, menu):
        self.menus[obj.name] = menu #register
        self.add(menu) #add to graphics queue
        
    # Quit program for now.
    def option_quit(self):
        pygame.event.post(pygame.event.Event(QUIT))

    def option_move(self):
        self.data.mode = I_MOVE
        character = self.data.selected
        speed = self.level.creatures[character].speed
        accessible = self.map.generate_accessible(character, speed)
        self.highlight.set_tiles(accessible)
        self.highlight.on()

    def option_attack(self):
        print "Attack"

    def determine_hover_square(self, mouse_coords, map_offset):
        x = mouse_coords[0]-map_offset[0] - self.off_x
        y = mouse_coords[1]-map_offset[1]
        
        new_x = x*cos(self.theta_x) + y*sin(self.theta_x)
        new_y = -x*sin(self.theta_y) + y*cos(self.theta_y)
        
        if 0 < new_x < self.max_x and 0 < new_y < self.max_y:
            hov_x = int(new_x/self.hyp)
            hov_y = int(new_y/self.hyp)
            self.data.hover = hov_x, hov_y
            self.hover_tile.set_pos(self.data.hover)            

    #set selected and current menu to the one specified by given coordinates.
    def set_selected_object(self, pos):
        x,y,z = pos
        if self.map.grid[x][y]:
            name = self.map.grid[x][y].name
            self.data.selected = name
            
            self.current_menu = self.menus[name]
        else:
            self.current_menu = None

    def browse_right_click(self, mouse_coords):
        if not self.current_menu:
            self.current_menu = self.main_menu_placed
            self.hover_tile.make_invisible()
               
        if not self.current_menu.visible:
            self.current_menu.set_pos(mouse_coords)
            self.current_menu.make_visible()
        else:
            self.current_menu.make_invisible()
            self.current_menu = None
            self.hover_tile.make_visible()

    def browse_left_click(self, mouse_coords):
        if not self.current_menu:
            self.set_selected_object(self.hover_tile.pos)
            if self.current_menu:
                self.hover_tile.make_invisible()
                self.current_menu.make_visible()
                self.current_menu.set_pos(mouse_coords)
        else:
            if not self.current_menu.visible:
                self.current_menu.make_visible()
                self.current_menu.set_pos(mouse_coords)
            else:
                self.current_menu.obj.log_pending()

    def browse_left_release(self, mouse_coords):
        if self.current_menu and self.current_menu.obj.pending != None:
            self.current_menu.obj.execute_entry()
            self.current_menu.obj.clear_pending()
            self.current_menu.make_invisible()
            self.hover_tile.make_visible()
            #self.current_menu = None
    
    def move_right_click(self, mouse_coords):
        self.data.mode = I_BROWSE

    def move_left_click(self, mouse_coords):
        pass

    def move_left_release(self, mouse_coords):
        x,y,z = self.hover_tile.pos
        if (x,y) in self.highlight.set:
            pygame.event.post(Move_Event(self.data.selected, (x,y)))
            self.data.locked = True
            self.current_menu = None
            self.highlight.off()

    def set_browse(self):
        self.data.dest = None
        self.data.mode = I_BROWSE
        self.data.locked = False

    def unlock(self):
        self.data.locked = True

    def update(self, mouse_coords, mouse_state, keybuffer, map_offset):
        new_left, new_middle, new_right = mouse_state
        #what to execute depends on the previous and current mouse states
        if not self.data.locked:
            if new_right and not self.right:
                if self.data.mode == I_BROWSE:
                    self.browse_right_click(mouse_coords)
                elif self.data.mode == I_MOVE:
                    self.move_right_click(mouse_coords)

            if new_left and not self.left:
                if self.data.mode == I_BROWSE:
                    self.browse_left_click(mouse_coords)
        
            if not new_left and self.left:
                if self.data.mode == I_BROWSE:
                    self.browse_left_release(mouse_coords)
                elif self.data.mode == I_MOVE:
                    self.move_left_release(mouse_coords)
        
        self.determine_hover_square(mouse_coords, map_offset)

        # now we can update the mouse state
        self.left, self.middle, self.right = mouse_state
        self.mouse_coords = x,y = mouse_coords
        
        if self.current_menu:
            x2, y2, z2 = self.current_menu.get_pos()
            rel_coords = (x-x2,y-y2)
            self.current_menu.obj.update(rel_coords)

def UI_Event(self, subtype=None):
    e = pygame.event.Event(UI_EVENT)
    e.subtype = subtype
    return e

# Notify creature's intention to move to a certain destination.
def Move_Event(creature=None, destination=None):
    e = pygame.event.Event(UI_EVENT, subtype=MOVETO, name=creature, dest=destination)
    return e
        
def End_Turn_Event():
    e = pygame.event.Event(UI_EVENT, subtype=ENDTURN)
    return e

class UIData:
    def __init__(self):
        self.mode = I_BROWSE
        self.hover = None
        self.locked = False

        self.selected = None
        self.dest = None

class StatusWindow:
    gfx = "./content/gfx/gui/"
    """Collection of elements that describe character/monster"""
    def __init__(self):
        self.portrait = Graphic("./content/gfx/sprites/reimu_portrait.png")
        self.stats = None
        self.health_bar = HorizontalBar(self.gfx+"health_bar.png")
        self.visible = True

        self.elements = []

        self.add_element(self.health_bar,(120.0, 50.0))
        self.add_element(self.portrait,(0.0,0.0))

    def add_element(self, element, position):
        self.elements += [(element, position)]

    def load_stats(self, stats):
        self.stats = stats
        self.health_bar.load_stats(self.stats.hp, self.stats.MAX_HP)
        self.visible = True

    def window_off(self):
        self.visible = False

    def update(self):
        self.health_bar.set_value(self.stats.hp)

    def draw(self):
        for e in self.elements:
            element, position = e
            x,y = position
            glPushMatrix()
            glTranslate(x,y,0)
            element.draw()
            glPopMatrix()


class HorizontalBar:
    """Bar that has a length that depends on the value, eg. a health bar"""
    def __init__(self, image, length=100.0):
        self.image = Graphic(image)
        self.base_length = float(length)
        self.image.w = self.base_length
        self.image.setup_draw()
        self.max_value = None
        self.current_value = None

    def load_stats(self, current_value, max_value):
        self.current_value = current_value
        self.max_value = max_value

    def set_value(self, value):
        self.current_value = float(value)
        self.image.w = self.current_value/self.max_value * self.base_length

    def set_max(self, max_value):
        self.max_value = float(max_value)

    def draw(self):
        self.image.draw()
