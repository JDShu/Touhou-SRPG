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
from collections import deque
from OpenGL.GL import *

class GfxManager:
    def __init__(self):
        self.draw_pending = deque()
        self.x, self.y = 0,0 #probably needs to be removed

    def register_draw(self, graphic):
        self.draw_pending.append(graphic)
        
    def shift(self,value):
        self.x, self.y = self.x+value[0], self.y+value[1]

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glPushMatrix()
        glTranslate(self.x,self.y,0)
        while self.draw_pending:
            graphic = self.draw_pending.popleft()
            graphic.draw()
        glPopMatrix()
        pygame.display.flip()
