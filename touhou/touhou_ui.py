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
from math import *

from core.graphics.graphic import Graphic, GraphicPositioned, GraphicAbsPositioned
from core.ui import UI, Menu

from touhou_graphic import MapGraphic
#from core.misc.glFreeType import pushScreenCoordinateMatrix, pop_projection_matrix

class TouhouUI(UI):
    def __init__(self, touhou_map):
        self.map_x, self.map_y = touhou_map.w, touhou_map.h
        self.off_x, self.off_y = touhou_map.TILE_OFFSET[0], touhou_map.TILE_OFFSET[1]
        
        self.off_x = float(self.off_x)
        self.off_y = float(self.off_y)
                
        self.theta_x = atan(self.off_x/self.off_y)
        
        self.theta_y = atan(self.off_y/self.off_x)
        self.hyp = hypot(self.off_x, self.off_y)
        
        UI.__init__(self)
        self.menu = Menu("Test")
        self.left, self.middle, self.right = (0,0,0)
        self.menu.set_body_graphic("./content/gfx/gui/menu_body.png")
        self.menu.set_entry_hover_graphic("./content/gfx/gui/menu_option.png")
        self.menu.set_w(80)
        self.menu.set_header_height(30)
        self.menu.set_entry_height(30)
        
        self.menu.add_entry("Move", self.option_move)
        self.menu.add_entry("Attack", self.option_attack)

        self.menu_placed = GraphicAbsPositioned(self.menu,(0,0))
        hover_graphic = Graphic("./content/gfx/sprites/hover.png", 0.5)
        self.hover_tile = MapGraphic(hover_graphic, (0,0))
        self.hover_tile.make_visible()
        self.add(self.menu_placed)
        self.add(self.hover_tile)
        

    def option_move(self):
        print "Move"

    def option_attack(self):
        print "Attack"

    def determine_hover_square(self, mouse_coords, map_offset):
        x = mouse_coords[0]-map_offset[0] - self.off_x
        y = mouse_coords[1]-map_offset[1]
        
        new_x = x*cos(self.theta_x) + y*sin(self.theta_x)
        new_y = -x*sin(self.theta_y) + y*cos(self.theta_y)
        
        hov_x = int(new_x/self.hyp)
        hov_y = int(new_y/self.hyp)

        self.hover_tile.set_pos((hov_x, hov_y))

    def update(self, mouse_coords, mouse_state, keybuffer, map_offset):
        new_left, new_middle, new_right = mouse_state

        #what to execute depends on the previous and current mouse states
        if new_right and not self.right:
            if not self.menu_placed.visible:
                self.menu_placed.set_pos(mouse_coords)
                self.menu_placed.make_visible()
            else:
                self.menu_placed.make_invisible()
                
        if new_left and not self.left:
            self.menu.log_pending()

        if not new_left and self.left:
            self.menu.execute_entry()

        self.determine_hover_square(mouse_coords, map_offset)

        # now we can update the mouse state
        self.left, self.middle, self.right = mouse_state
        self.mouse_coords = x,y = mouse_coords
        x2, y2, z2 = self.menu_placed.get_pos()
        rel_coords = (x-x2,y-y2)
        
        self.menu.update(rel_coords)

class StatusWindow:
    gfx = "./content/gfx/gui/"
    """Collection of elements that describe character/monster"""
    def __init__(self, coords):
        self.portrait = None
        self.stats = None
        self.health_bar = HorizontalBar(self.gfx+"health_bar.png")
        self.visible = False
        self.coords = coords

    def load_stats(self, stats):
        self.stats = stats
        self.health_bar.load_stats(self.stats.hp, self.stats.MAX_HP)
        self.visible = True

    def window_off(self):
        self.visible = False

    def update(self):
        self.health_bar.set_value(self.stats.hp)

    def draw(self):
        x,y = self.coords
        if self.visible:
            self.stats.portrait.draw(x,y)
            x += 150
            y += 70
            self.health_bar.draw(x,y)

class HorizontalBar:
    """Bar that has a length that depends on the value, eg. a health bar"""
    def __init__(self, image):
        self.image = core.objects.DynamicGraphic(1.0, image)
        self.image.w = 300.0
        self.image.setup_draw()
        self.max_value = None
        self.current_calue = None
        

    def load_stats(self, current_value, max_value):
        self.current_value = current_value
        self.max_value = max_value

    def set_value(self, value):
        self.current_value = value

    def draw(self, x, y):
        self.image.draw(x, y)
    
