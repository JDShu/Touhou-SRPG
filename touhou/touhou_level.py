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

from core.graphics.graphic import Graphic, GraphicPositioned, GraphicList
from core.graphics.common import Repeated
from core.graphics.animated import Animated

from touhou_graphic import MapGraphic

#From touhou_character import Reimu

#Touhou Level State, includes information about the map, characters, monsters, etc.
#Theoretically can be for load games, saved games, and level editors
class TouhouLevel:
    def __init__(self):
        self.characters = {}
        self.monsters = {}
        # test code
        self.map = TouhouMap()
        self.map.setup_map(10,10)

class TouhouMap:
    TILE_OFFSET = (45.0,30.0)
    TILE_DIMENSIONS = (90.0,60.0)
    TILE_DATA = (TILE_OFFSET, TILE_DIMENSIONS)
    def __init__(self):
        self.obj_list = []
        self.grid = []
        self.ground_tile = Graphic(texture="./content/gfx/sprites/grass.png")
        
        # test code starts here
        self.setup_map(10,10) 
        test_tree = Graphic(texture="./content/gfx/sprites/tree.png")
        for x in xrange(4):
            for y in xrange(4):
                self.place_object(test_tree,(x,y))
        # test code ends here
        self.ground = None
        self.setup_ground()
                
    def set_ground_tile(self, tile):
        self.ground_tile = tile
        self.setup_ground()

    def setup_ground(self):
        self.ground = Repeated((self.w, self.h),self.TILE_OFFSET, self.ground_tile)
        self.ground = GraphicPositioned(self.ground, (0,0))
        self.ground.make_visible()

    def setup_map(self, w, h):
        self.w, self.h = w, h
        for y in xrange(self.h):
            temp = []
            for x in xrange(self.w):
                temp += [None]
            self.grid += [temp]

    # update the data for each game object first, then update the new map
    def update(self,e):
        #update each object
        for x in xrange(self.w):
            for y in xrange(self.h):
                old_x, old_y = self.w-x-1, self.h-y-1
                obj = self.grid[old_x][old_y]
                if obj:
                    self.update_obj(obj, e, (old_x, old_y))
                    
    # update the map position for an object if its position has changed
    def update_obj(self, obj, e, old_coords):
        obj.update(e)
        if obj.pos != old_coords:
            x, y = obj.pos
            self.grid[x][y] = obj
            x2, y2 = old_coords
            self.grid[x2][y2] = None
                        
    def draw(self):
        temp = GraphicList()
        temp.add(self.ground)
        for x in xrange(self.w):
            for y in xrange(self.h):
                if self.grid[self.w-x-1][self.h-y-1]:
                    temp.add(self.grid[self.w-x-1][self.h-y-1])
        return temp
    
    def place_object(self, obj, pos, details=None):
        temp = MapGraphic(obj,pos,details)
        self.grid[pos[0]][pos[1]] = temp
        self.obj_list += [temp]
        
    def remove_object(self, tup):
        self.grid[tup[0]][tup[0]] = None

    def relocate_object(self, obj_tup, pos):
        self.place_object(obj_tup[0], pos)
        self.remove_object(obj_tup[1])


