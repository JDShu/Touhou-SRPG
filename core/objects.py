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
from OpenGL.GL import *
from OpenGL.GLU import *
from math import *
import pickle
import sprite_rules

import level
import astar
import copy
import collections

TILE_DIMENSIONS = TILE_BASE, TILE_HEIGHT = level.TILE_DIMENSIONS
TILE_OFFSETS = level.TILE_OFFSETS
ratio = sqrt(pow(TILE_DIMENSIONS[0],2) + pow(TILE_DIMENSIONS[1],2))
INC_UP = TILE_DIMENSIONS[0]/ratio
INC_ACROSS = TILE_DIMENSIONS[1]/ratio

def square_to_screen(x,y):
    base, height = TILE_DIMENSIONS
    width_offset, height_offset = TILE_OFFSETS
    return -(x+y-0.5)*width_offset + base*x, (x-y+1)*height_offset + height*y


class Graphic:
    def __init__( self, a, texture = None, scale_factor = 1.0, w = None, h = None):
        self.a = a
        self.texture = texture
        texture_surface = pygame.image.load(texture)
        texture_data = pygame.image.tostring( texture_surface, "RGBA", 1 )
        self.w = texture_surface.get_width()
        self.h = texture_surface.get_height()
        self.texture = glGenTextures(1)
        glBindTexture( GL_TEXTURE_2D, self.texture )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST )
        # OpenGL < 2.0 hack
        #gluBuild2DMipmaps( GL_TEXTURE_2D, GL_RGBA, self.w, self.h, GL_RGBA, GL_UNSIGNED_BYTE, texture_data )
        # OpenGL >= 2.0
        glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, self.w, self.h, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data )

        if w:
            self.w = w
        if h:
            self.h = h
        
        self.w *= scale_factor
        self.h *= scale_factor
        
        #pregenerate render code
        self.draw_list = glGenLists(2)
        self.setup_draw()
        
      
    def setup_draw( self ):
        
        glNewList(self.draw_list, GL_COMPILE)
        glPushMatrix()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        color = (1.0,1.0,1.0,self.a)
        glEnable( GL_TEXTURE_2D )
        glBindTexture( GL_TEXTURE_2D, self.texture )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR )
        glColor4f(*color)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex(0.0,0.0,0.0)
        glTexCoord2f(1.0, 0.0)
        glVertex(self.w,0.0,0.0)
        glTexCoord2f(1.0, 1.0)
        glVertex(self.w,self.h,0.0)
        glTexCoord2f(0.0, 1.0)
        glVertex(0.0,self.h,0.0)
        glEnd()
        glDisable( GL_TEXTURE_2D )
        glDisable( GL_BLEND)
        glPopMatrix()
        
        glEndList()
        
    def draw( self, x,y ):
        glPushMatrix()
        glTranslatef(x,y,0.0)
        glCallList(self.draw_list)
        glPopMatrix()

    def draw_grid(self, x, y, dimensions, offsets):
        w,h = dimensions
        x_offset, y_offset = offsets
        glPushMatrix()
        self.draw(x*w + (y-x)*x_offset, -y*h + (x+y)*y_offset)
        glPopMatrix()

    def process_click(self):
        pass

class DynamicGraphic(Graphic):
    def __init__(self, a, texture = None, scale_factor = 1.0, w = None, h = None):
        Graphic.__init__(self, a, texture, scale_factor, w, h)
        
    def setup_draw(self):
        self.v_array = [(0.0,0.0),(self.w,0.0),(self.w,self.h),(0.0,self.h)]
        self.indices = range(4)
        self.t_array = [(0.0,0.0),(1.0,0.0),(1.0,1.0),(0.0,1.0)]

    def draw(self,x,y):
        glPushMatrix()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        color = (1.0,1.0,1.0,self.a)
        
        glEnable( GL_TEXTURE_2D )
        glBindTexture( GL_TEXTURE_2D, self.texture )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR )
        glColor4f(*color)
        
        glTranslatef(x,y,0.0)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY);
        glVertexPointer(2, GL_FLOAT, 0, self.v_array)
        glTexCoordPointer(2, GL_FLOAT, 0, self.t_array)
        glDrawElements(GL_QUADS, 4, GL_UNSIGNED_BYTE, self.indices);
        glDisableClientState(GL_VERTEX_ARRAY);
        glDisableClientState(GL_TEXTURE_COORD_ARRAY);
        
        glDisable( GL_TEXTURE_2D )
        glDisable( GL_BLEND)
        
        glPopMatrix()


class Tile(Graphic):
    def __init__(self, image_file):
        Graphic.__init__(self, 1.0, image_file)
        
    def draw(self, x, y):
        """draw according to coordinate on grid"""
        glPushMatrix()
        Graphic.draw(self, x*self.w + (y-x)*self.x_offset, -y*self.h + (x+y)*self.y_offset)
        glPopMatrix()


class Animated(Graphic):
    def __init__(self, x,y,sprite_name, scale_factor = 1.0):
        self.a = 1.0
        self.x, self.y = x,y
        
        self.set_sprite(sprite_name)
        self.current_action = "idle-s"
        self.current_frame_number = 0
        self.current_frame_dimensions = self.data.actions[self.current_action][self.current_frame_number]
        self.action = None
        self.w, self.h = float(self.current_frame_dimensions[2]), float(self.current_frame_dimensions[3])
        self.w *= scale_factor
        self.h *= scale_factor
        self.scale_factor = scale_factor
        
    def set_action(self, action):
        self.current_action = action

    def set_sprite(self, sprite_name):
        try:
            self.data = pickle.load(open(sprite_name + ".spr"))
        except IOError:
            self.data = pickle.load(open(sprite_name + ".spr", "wb"))
            
        texture_surface = pygame.image.load(sprite_name + ".png")
        texture_data = pygame.image.tostring( texture_surface, "RGBA", 1 )
        
        self.image = glGenTextures(1)
        glBindTexture( GL_TEXTURE_2D, self.image )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST )
        self.tex_w, self.tex_h = texture_surface.get_width(), texture_surface.get_height()
        # OpenGL < 2.0 hack
        #gluBuild2DMipmaps( GL_TEXTURE_2D, GL_RGBA, self.w, self.h, GL_RGBA, GL_UNSIGNED_BYTE, texture_data )
        # OpenGL >= 2.0
        glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, self.tex_w, self.tex_h, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data )


    def update(self):
        self.current_frame_number += 1
        try:
            self.current_frame_dimensions = self.data.actions[self.current_action][self.current_frame_number]
        except IndexError:
            self.current_frame_number = 0
            self.current_frame_dimensions = self.data.actions[self.current_action][self.current_frame_number]
        self.w, self.h = self.current_frame_dimensions[2]*self.scale_factor, self.current_frame_dimensions[3]*self.scale_factor
        

    def draw( self,x,y ):
        glTranslatef(x + self.x, y + self.y,0.0)
        pix_x,pix_y,pix_w,pix_h = self.current_frame_dimensions
        x = float(pix_x)/float(self.tex_w)
        y = float(pix_y)/float(self.tex_h)
        w = float(pix_w)/float(self.tex_w)
        h = float(pix_h)/float(self.tex_h)
        y = 1.0 - y - h
        
        glPushMatrix()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        color = (1.0,1.0,1.0,1.0)
        glEnable( GL_TEXTURE_2D )
        glBindTexture( GL_TEXTURE_2D, self.image )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR )
        
        
        #draw
        glColor4f(*color)
        glBegin(GL_QUADS)
        glTexCoord2f(x, y)
        glVertex(0.0,0.0,0.0)
        glTexCoord2f(x + w, y)
        glVertex(self.w,0.0,0.0)
        glTexCoord2f(x + w, y + h)
        glVertex(self.w,self.h,0.0)
        glTexCoord2f(x, y + h)
        glVertex(0.0,self.h,0.0)
        glEnd()
        glDisable( GL_TEXTURE_2D )
        glDisable( GL_BLEND)
        glPopMatrix()


