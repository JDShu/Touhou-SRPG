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
from pygame.locals import *
from collections import deque
from OpenGL.GL import *

from session import Session

# Handles keyboard/mouse and basic drawing
class IOSession(Session):
    def __init__(self):
        Session.__init__(self)

        display = pygame.display.get_surface()
        self.h = display.get_height()

        self.keybuffer = self.new_keybuffer()
        self.mouse_coords = None
        self.draw_pending = deque()

        self.register_event(KEYDOWN, self.key_down)
        self.register_event(KEYUP, self.key_up)
        self.register_event(MOUSEBUTTONDOWN, self.update_mouse)
        self.register_event(MOUSEBUTTONUP, self.update_mouse)
        self.register_event(MOUSEMOTION, self.update_mouse)

    def new_keybuffer(self):
        keybuffer = []
        for i in range(320):
            keybuffer.append( False )
        return keybuffer

    def key_down(self, e):
        self.keybuffer[e.key] = True

    def key_up(self, e):
        self.keybuffer[e.key] = False

    def update_mouse(self, e):
        x, y = e.pos
        y = self.h - y
        self.mouse_coords = x, y
        self.mouse_state = pygame.mouse.get_pressed()

    def register_draw(self, graphic):
        if graphic:
            self.draw_pending.append(graphic)

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT)
        while self.draw_pending:
            graphic = self.draw_pending.popleft()
            graphic.draw()
        pygame.display.flip()
    
    def shift(self,value):
        glTranslate(value[0],value[1],0)
