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
import pygame
from math import *

import level
#import events
import ui
import glFreeType
from objects import *
import actions
import stats
import astar

SCALE = 0.5

BROWSE, MOVE, ATTACK = xrange(3)

class Play:
    """Play Session that is run each game loop """
    def __init__(self, module, module_map):
        """
        key arguments:
        module: The Game module that is to be run on the engine.
        module_map: The Map that will be passed into the Game Module.

        Variables:
        session: specific module that runs on iso engine
        keybuffer: The Keyboard Buffer

        """
        self.new_keybuffer()
        self.session = module.play(module_map)
        display = pygame.display.get_surface()
        self.h = display.get_height()
        self.left_offset, self.up_offset = 0,0

    def new_keybuffer(self):
        """Clears Keyboard Buffer"""
        self.keybuffer = []
        for i in range(320):
            self.keybuffer.append( False )
        
    def process( self ):
        """One pass of the play session loop of the running module"""
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_y = self.h - mouse_y
        mouse_coords = mouse_x, mouse_y
        mouse_state = pygame.mouse.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                self.keybuffer[ event.key ] = True
            elif event.type == pygame.KEYUP:
                self.keybuffer[ event.key ] = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pass
            elif event.type == pygame.MOUSEBUTTONUP:

                # what got clicked
                self.session.process_click(mouse_coords, mouse_state)
                
            else:
                self.session.process_event(event, mouse_coords, mouse_state)
                
        self.session.process_keybuffer(self.keybuffer)
                
        return True
    
    def draw( self ):
        """ Draw everything after one pass of the module loop is processed"""
        
#draw map
        glPushMatrix()
        glTranslatef(self.left_offset,self.up_offset,0.0)
        self.session.draw_relative()
        
        glPopMatrix()
        glPushMatrix()
        self.session.draw_absolute()
        glPopMatrix()

    def get_mouse_square(self, mouse_x, mouse_y ):
        
        t_offsets = self.play_state.level.tile_offsets
        t_dimensions = self.play_state.level.tile_dimensions
        mouse_x -= self.left_offset + t_offsets[0]
        mouse_y -= self.up_offset
        theta1 = atan(t_offsets[0]/t_offsets[1])
        theta2 = atan(t_offsets[1]/t_offsets[0])
        x = mouse_x*cos(theta1) + mouse_y*sin(theta1)
        y = -mouse_x*sin(theta2) + mouse_y*cos(theta2)
        max_x = self.tile_w*(self.play_state.level.w-1)
        max_y = self.tile_h*(self.play_state.level.h-1)
        if 0 < x < max_x and 0 < y < max_y:
            return floor((x/max_x)*self.play_state.level.w), floor((y/max_y)*self.play_state.level.h)
        else:
            return False
