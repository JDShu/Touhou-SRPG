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
        
