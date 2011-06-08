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
import pygame
import pickle

from graphic import Graphic
# Animates sprites by looping through graphics
# TODO: Break up so that an animated object just does one loop.
class DeprecatedAnimated(Graphic):
    metafolder = "./content/metadata/"
    gfx = "./content/gfx/sprites/"
    def __init__(self, sprite_name, scale_factor = 1.0):
        self.a = 1.0
                
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
            self.data = pickle.load(open(self.metafolder + sprite_name + ".spr"))
        except IOError:
            self.data = pickle.load(open(self.metafolder + sprite_name + ".spr", "wb"))
            
        texture_surface = pygame.image.load(self.gfx+sprite_name+".png")
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

    #event handler for updating frame
    def update(self, e):
        self.current_frame_number += 1
        try:
            self.current_frame_dimensions = self.data.actions[self.current_action][self.current_frame_number]
        except IndexError:
            self.current_frame_number = 0
            self.current_frame_dimensions = self.data.actions[self.current_action][self.current_frame_number]
        self.w, self.h = self.current_frame_dimensions[2]*self.scale_factor, self.current_frame_dimensions[3]*self.scale_factor
        

    def draw( self ):
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

