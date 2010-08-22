import pygame

import level
from objects import *

#map file, scenario file, characters
class Play:
    def __init__( self ):
        self.level = None
        self.new_keybuffer()
        self.animation_test = Actor(0.0,0.0,1.0,9,2,"reimu2.png")
        
    def new_keybuffer( self ):
        self.keybuffer = []
        for i in range(320):
            self.keybuffer.append( False )
        
    def process( self ):
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                self.keybuffer[ event.key ] = True
            elif event.type == pygame.KEYUP:
                self.keybuffer[ event.key ] = False
            elif event.type == pygame.USEREVENT + 1:
                self.animation_test.update()
                
        if self.keybuffer[pygame.K_UP]:
            glTranslate(0.0,3.0,0.0)
        if self.keybuffer[pygame.K_DOWN]:
            glTranslate(0.0,-3.0,0.0)
        if self.keybuffer[pygame.K_LEFT]:
            glTranslate(-3.0,0.0,0.0)
        if self.keybuffer[pygame.K_RIGHT]:
            glTranslate(3.0,0.0,0.0)
        return True
    
    def draw( self ):
        #draw map
        self.draw_map()
        self.animation_test.Draw()
        
    def load_map( self, level_map ):
        pass

    def draw_map( self ):
        for x in xrange(self.level.w):
            for y in xrange(self.level.h):
                self.level.ground_tile.set_pos(x,y)
                self.level.ground_tile.Draw()
                
    def load_level( self, level ):
        self.level = level
        self.animation_test.set_pos(3,3,self.level.tile_settings)
