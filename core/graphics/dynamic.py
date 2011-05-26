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

from graphic import Graphic
import core.sprite_rules
#import level

# Uses vertex arrays and so can be updated directly.
# TODO: switch to VBOs for speed
class DynamicGraphic(Graphic):
    def __init__(self, a = 1.0, texture = None, scale_factor = 1.0, w = None, h = None):
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
