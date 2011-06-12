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
from core.graphics.animated import Graphic, Animated
import core.misc.astar
import copy

CHARACTER, MONSTER, OBSTACLE = range(3)

class Stats:
    gfx = "./content/gfx/sprites/"
    """Collection of statistics describing actor"""
    def __init__(self, hp, ap, portrait):
        self.MAX_HP = hp
        self.MAX_AP = ap
        self.hp = hp
        self.ap = ap
        self.portrait = Graphic(1.0, self.gfx+portrait)

    def restore_ap(self):
        self.ap = self.MAX_AP

    def restor_hp(self):
        self.hp = self.MAX_HP

class Actor(Animated):
    """An Actor is anything that influences the game, usually a character or monster"""
    MOVING, IDLE = range(2)
    TICKS = 5
    def __init__(self, x,y,sprite_name, position, touhou_map, touhou, scale_factor = 1.0):
        DeprecatedAnimated.__init__(self, x, y, sprite_name, scale_factor)
        self.selected = False
        self.set_cell_offsets(0,0)
        self.position = position
        self.state = self.IDLE
        self.tile_offsets = touhou_map.offsets
        self.map = touhou_map
        self.path = []
        self.direction = None
        self.ticks = 0
        self.play = touhou

    def process_click(self, mouse_coords, mouse_state):
        print "process_click not implemented"

    def draw_grid(self, x, y, dimensions, offsets):
        glPushMatrix()
        glTranslatef(self.cell_offset_x, self.cell_offset_y, 0.0)
        Animated.draw_grid(self, x, y, dimensions, offsets)
        glPopMatrix()
        
    def set_cell_offsets(self, x, y):
        self.cell_offset_x, self.cell_offset_y = x, y

    def mod_cell_offsets(self, x, y):
        self.cell_offset_x += x
        self.cell_offset_y += y

    def move_cell(self, direction):
        self.state = self.MOVING
        self.direction = direction
        self.ticks = 0

    def move_inc(self):
        """Move subject incrementally in a direction until it reaches one cell away"""
        if self.direction == "N":
            d = (1,1) 
            p = (1,0)
        elif self.direction == "S":
            d = (-1,-1)
            p = (-1,0)
        elif self.direction == "E":
            d = (1,-1)
            p = (0,1)
        elif self.direction == "W":
            d = (-1,1)
            p = (0,-1)
        else:
            d = (0,0)
            p = (0,0)

        self.mod_cell_offsets(d[0]*self.tile_offsets[0]/self.TICKS, d[1]*self.tile_offsets[1]/self.TICKS)
        self.ticks += 1
        #print self.ticks
        if self.ticks >= self.TICKS:
            #self.state = self.IDLE
            self.map.relocate(self, (self.position[0] + p[0],self.position[1] + p[1]))
            self.set_cell_offsets(0.0,0.0)
            self.path = self.path[:-1]
            self.move_to_destination()
            self.ticks = 0
                        

    def move_to_destination(self):
        
        if self.path:
            next_cell = self.path[-1]
            direction = next_cell[0] - self.position[0], next_cell[1] - self.position[1]
            
            if direction == (0,1):
                self.direction = "E"
                self.current_action = "idle-e"
            elif direction == (0,-1):
                self.direction = "W"
                self.current_action = "idle-w"
            elif direction == (1,0):
                self.direction = "N"
                self.current_action = "idle-n"
            elif direction == (-1,0):
                self.direction = "S"
                self.current_action = "idle-s"
            
        else:
            self.state = self.IDLE
            self.play.mode = self.play.BROWSE
            
        
    def update(self):
        Animated.update(self)
        if self.state == self.MOVING:
            self.move_inc()
        
        
    def new_path(self, touhou_map, destination):
        self.state = self.MOVING
        grid = core.astar.Grid(touhou_map)
        path = core.astar.Path(grid, self.position, [destination])
        self.path = [(5,4)]
        self.path = path.path
        self.move_to_destination()

class StaticObject(Graphic):
    def __init__(self, a, texture = None, scale_factor = 1.0, w = None, h = None):
        Graphic.__init__(self, a, texture, scale_factor, w, h)

    def process_click(self, mode):
        pass

class PlayerCharacter(Actor):
    def __init__(self, x,y,sprite_name, position, touhou_map, touhou, scale_factor = 1.0):
        Actor.__init__(self, x,y,sprite_name, position, touhou_map, touhou, scale_factor = 1.0)
        self.menu = None
        self.type = CHARACTER

    def set_menu(self, menu):
        self.menu = menu
        
    def move_inc(self):
        Actor.move_inc(self)
        
    def update(self, mouse_coords, mouse_state):
        Actor.update(self)
        self.menu.update(mouse_coords, mouse_state)

    def process_click(self, mouse_coords, mouse_state):
        self.menu.set_pos(*mouse_coords)
        self.menu_on()

    def menu_on(self):
        """Turn the menu on """
        self.menu.menu_on()

    def menu_off(self):
        """Turn the menu off"""
        self.menu.menu_off()


