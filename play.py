import pygame

import level
import events
import ui
from objects import *

SCALE = 0.5

#map file, scenario file, characters
class Play:
    def __init__( self, w,h ):
        self.level = None
        self.new_keybuffer()
        self.animation_test = Actor(0.0,0.0,1.0,9,2,"reimu2.png", SCALE)
        self.test_menu = ui.Menu("test")
        self.w, self.h = w, h
        self.left_offset, self.up_offset = 0, 0
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                mouse_y = self.h - mouse_y
                l_click, m_click, r_click = pygame.mouse.get_pressed()
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                mouse_y = self.h - mouse_y
                l_click, m_click, r_click = pygame.mouse.get_pressed()
                self.test_menu.set_pos(mouse_x, mouse_y)

        if self.keybuffer[pygame.K_UP]:
            self.up_offset -= 3.0
        if self.keybuffer[pygame.K_DOWN]:
            self.up_offset += 3.0
        if self.keybuffer[pygame.K_LEFT]:
            self.left_offset += 3.0
        if self.keybuffer[pygame.K_RIGHT]:
            self.left_offset -= 3.0
        
        return True
    
    def draw( self ):
        #draw map
        glPushMatrix()
        glTranslatef(self.left_offset,self.up_offset,0.0)
        self.draw_map()
        self.animation_test.Draw()
        glPopMatrix()
        self.test_menu.Draw()
        
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
