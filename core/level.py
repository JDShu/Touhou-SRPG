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
SCALE = 0.8
TILE_DIMENSIONS = TILE_BASE, TILE_HEIGHT = SCALE*90, SCALE*60
TILE_OFFSETS = WIDTH_OFFSET, HEIGHT_OFFSET = SCALE*45, SCALE*30

from objects import *

class Level:
    def __init__( self, width, height ):
        self.w, self.h = width, height
        self.map = []
        for y in xrange(height):
            temp = []
            for x in xrange(width):
                temp += [None]
            self.map += [temp]
        self.tile_dimensions = TILE_DIMENSIONS
        self.tile_offsets = TILE_OFFSETS
        self.ground_tile = Tile(0.0,0.0,1.0,TILE_BASE, TILE_HEIGHT, WIDTH_OFFSET, HEIGHT_OFFSET,"grass.png", SCALE)
        self.hover_tile = Tile(0.0,0.0,0.5,TILE_BASE, TILE_HEIGHT, WIDTH_OFFSET, HEIGHT_OFFSET,"hover.png", SCALE)
        
    def print_map( self ):
        for r in reversed(self.map):
            print r
            
    def insert( self, coords, item ):
        if 0 <= coords[0] < self.w and 0 <= coords[1] < self.h:
            self.map[coords[0]][coords[1]] = item

    def remove (self, coords ):
        self.map[coords[0]][coords[1]] = None
            
    def relocate (self, before, after, item):
        self.remove(before)
        self.insert(after,item)
        
    def move( self, before, after ):
        self.map[after[0]][after[1]] = self.map[before[0]][before[1]]
        self.map[before[0]][before[1]] = None
        
