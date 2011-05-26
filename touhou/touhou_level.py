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

from touhou_map import TouhouMap
from core.graphics.graphic import Graphic, GraphicPositioned, GraphicList
from core.graphics.common import Repeated

#Touhou Level State, includes information about the map, characters, monsters, etc.
#Theoretically can be for load games, saved games, and level editors
class TouhouLevel:
    def __init__(self):
        self.characters = {}
        self.monsters = {}
        self.map = TouhouMap()
        self.map.setup_map(10,10)

class TouhouMap:
    TILE_OFFSET = (45,30)
    TILE_DIMENSIONS = (90,60)
    TILE_DATA = (TILE_OFFSET, TILE_DIMENSIONS)
    def __init__(self):
        self.grid = []
        self.ground_tile = Graphic(texture="./content/gfx/sprites/grass.png")
        self.test_tile = GraphicPositioned(self.ground_tile, (100,100))
        self.setup_map(10,10) #test
        self.ground = None
        self.setup_ground()
        
        
                
    def set_ground_tile(self, tile):
        self.ground_tile = tile
        self.setup_ground()

    def setup_ground(self):
        self.ground = Repeated((self.w, self.h),self.TILE_OFFSET, self.ground_tile)
        pass

    def setup_map(self, w, h):
        self.w, self.h = w, h
        for y in xrange(self.h):
            temp = []
            for x in xrange(self.w):
                temp += [None]
            self.grid += [temp]

    def draw(self):
        temp = GraphicList()
        temp.add(GraphicPositioned(self.ground, (100,100))) #todo
        for y in xrange(self.h):
            for x in xrange(self.w):
                if self.grid[x][y]:
                    temp.add(self.grid[x][y])
        return temp
    
    def draw_ground(self):
        print "ground"

    def place_object(self, obj, pos):
        self.grid[pos[0]][pos[1]] = obj
        
    def remove_object(self, obj):
        self.grid[obj.x][obj.y] = None

    def move_object(self, obj, pos):
        self.place_object(obj, pos)
        self.remove_object(obj)
        self.object.change_pos(pos)
