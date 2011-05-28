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
from OpenGL.GLU import *
import pygame

# Basic graphic object that can be drawn
class Graphic:
    def __init__( self, texture = None, a = 1.0, scale_factor = 1.0, w = None, h = None):
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
        
        self.draw_list = glGenLists(2)
        self.setup_draw()

    def set_w(self,w):
        self.w = w
        self.setup_draw()
    
    def set_h(self,h):
        self.h = h
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
        
    def draw( self):
        glPushMatrix()
        glCallList(self.draw_list)
        glPopMatrix()
    
    # TODO: Needs to be moved to map
    #def draw_grid(self, x, y, dimensions, offsets):
    #    w,h = dimensions
    #    x_offset, y_offset = offsets
    #    glPushMatrix()
    #    self.draw(x*w + (y-x)*x_offset, -y*h + (x+y)*y_offset)
    #    glPopMatrix()

    def process_click(self):
        pass

class GraphicList:
    def __init__(self):
        self.g_list = []

    def add(self, graphic):
        self.g_list += [graphic]

    def set_list(self, g_list):
        self.g_list = g_list

    def draw(self):
        for g in self.g_list:
            g.draw()

class GraphicPositioned:
    def __init__(self, graphic, pos):
        self.graphic = graphic
        self.set_pos(pos)

    def set_pos(self,pos):
        self.pos = (pos[0],pos[1],0)

    def draw(self):
        glPushMatrix()
        glTranslate(*self.pos)
        self.graphic.draw()
        glPopMatrix()

class GraphicAbsPositioned(GraphicPositioned):
    def __init__(self, graphic, pos):
        GraphicPositioned.__init__(self, graphic, pos)
        self.viewport = glGetIntegerv(GL_VIEWPORT)

    def draw(self):
	glPushMatrix()
        glLoadIdentity()
        glOrtho(self.viewport[0], self.viewport[2], self.viewport[1], self.viewport[3],-1.0,1.0)        
        GraphicPositioned.draw(self)
        glPopMatrix()
