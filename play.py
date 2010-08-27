import pygame
from math import *

import level
import events
import ui
import glFreeType
from objects import *


SCALE = 0.5

#map file, scenario file, characters
class Play:
    def __init__( self, w,h ):
        self.level = None
        self.new_keybuffer()
        self.animation_test = Actor(0.0,0.0,1.0,9,2,"reimu2.png", SCALE)
        self.test_menu = ui.Menu("Title")
        def f(x):
            print x
        def g(x):
            print x + 1
        self.test_menu.add_entry(ui.Menu_Entry("1", f, "menu_option.png","menu_option_hover.png", "menu_option_clicked.png"))
        self.test_menu.add_entry(ui.Menu_Entry("2", g, "menu_option.png","menu_option_hover.png", "menu_option_clicked.png"))
        self.w, self.h = w, h
        self.font = glFreeType.font_data( "free_sans.ttf", 30 )

    def new_keybuffer( self ):
        self.keybuffer = []
        for i in range(320):
            self.keybuffer.append( False )
        
    def process( self ):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_y = self.h - mouse_y
        l_click, m_click, r_click = pygame.mouse.get_pressed()

        self.hover_square = self.get_mouse_square(mouse_x,mouse_y)
        print self.hover_square
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
                pass
            elif event.type == pygame.MOUSEBUTTONUP:
                if r_click:
                    self.test_menu.set_pos(mouse_x, mouse_y)
                    self.test_menu.toggle()
                elif l_click:
                    self.test_menu.process_click(1)
        #scroll around map
        if self.keybuffer[pygame.K_UP]:
            self.up_offset -= 3.0
        if self.keybuffer[pygame.K_DOWN]:
            self.up_offset += 3.0
        if self.keybuffer[pygame.K_LEFT]:
            self.left_offset += 3.0
        if self.keybuffer[pygame.K_RIGHT]:
            self.left_offset -= 3.0

        self.test_menu.update((mouse_x,mouse_y),l_click)
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
        if self.hover_square:
            self.level.hover_tile.set_pos(*self.hover_square)
            self.level.hover_tile.Draw()
            
    def load_level( self, level ):
        self.level = level
        self.left_offset, self.up_offset = 0, 0
        self.animation_test.set_pos(0,0,self.level.tile_dimensions, self.level.tile_offsets)
        
        
    def get_mouse_square(self, mouse_x, mouse_y ):
        #make sure mouse is in area
        t_offsets = self.level.tile_offsets
        t_dimensions = self.level.tile_dimensions
        

        mouse_x -= self.left_offset + t_offsets[0]
        mouse_y -= self.up_offset
        theta1 = atan(t_offsets[0]/t_offsets[1])
        theta2 = atan(t_offsets[1]/t_offsets[0])
        x = mouse_x*cos(theta1) + mouse_y*sin(theta1)
        y = -mouse_x*sin(theta2) + mouse_y*cos(theta2)
        w = sqrt(pow(t_offsets[0],2) + pow(t_offsets[1],2))
        h = w
        if 0 < x < w*(self.level.w-1) and 0 < y < h*(self.level.h-1):
            return floor((x/(w*(self.level.w-1)))*self.level.w), floor((y/(h*(self.level.h-1)))*self.level.h)
        else:
            return False
