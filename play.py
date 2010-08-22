import pygame

import level
from objects import *

#map file, scenario file, characters
class Play:
    def __init__( self ):
        self.level = None
        
    def process( self ):
        pass

    def draw( self ):
        #draw map
        self.draw_map()

    def load_map( self, level_map ):
        pass

    def draw_map( self ):
        for x in xrange(self.level.w):
            for y in xrange(self.level.h):
                self.level.ground_tile.set_pos(x,y)
                self.level.ground_tile.Draw()
                
    def load_level( self, level ):
        self.level = level
        
