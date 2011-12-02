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

import misc.glFreeType as glFreeType
from core.graphics.graphic import Graphic, GraphicList

class Menu:
    def __init__(self, title, data=None):
        self.title = title
        self.data = data

        self.entries = []
        self.body_graphic = None
        self.entry_graphic = None
        self.entry_hover_graphic = None
        self.set_font("./content/font/free_sans.ttf", 12)
        self.header_height = 0
        self.entry_height = 0
        self.hovering = None
        self.pending = None

    def set_body_graphic(self, graphic):
        self.body_graphic = Graphic(graphic)

    def set_w(self, w):
        self.w = w
        if self.body_graphic:
            self.body_graphic.set_w(self.w)
        if self.entry_graphic:
            self.entry_graphic.set_w(self.w)
        if self.entry_hover_graphic:
            self.entry_hover_graphic.set_w(self.w)

    def set_header_height(self, h):
        self.header_height = h
        self.h = self.header_height + len(self.entries) * self.entry_height
        self.body_graphic.set_h(self.h)

    def set_entry_height(self, h):
        self.entry_height = h
        self.h = self.header_height + len(self.entries) * self.entry_height
        if self.entry_graphic:
            self.entry_graphic.set_h(self.entry_height)
        if self.entry_hover_graphic:
            self.entry_hover_graphic.set_h(self.entry_height)

    def add_entry(self, name, function):
        self.entries += [(name,function)]
        self.h = self.header_height + len(self.entries) * self.entry_height
        self.body_graphic.set_h(self.h)

    def set_entry_graphic(self, graphic):
        self.entry_graphic = Graphic(graphic)

    def set_entry_hover_graphic(self, graphic):
        self.entry_hover_graphic = Graphic(graphic)

    def set_font(self,font,size):
        self.font = glFreeType.font_data(font,size)

    def draw(self):
        glPushMatrix()
        glTranslate(0, -self.h,0) #check later
        if self.body_graphic:
            self.body_graphic.draw()
        for index, entry in enumerate(self.entries):
            if self.hovering == index:
                if self.entry_hover_graphic:
                    self.entry_hover_graphic.draw()
            else:
                if self.entry_graphic:
                    self.entry_graphic.draw()
            glPushMatrix()
            glTranslate(0,self.font.m_font_height/2.0,0)
            self.print_text(entry[0])
            glPopMatrix()
            glTranslate(0, self.entry_height,0)

        self.print_text(self.title)

        glPopMatrix()

    def print_text(self, text):
        self.font.glPrint(0,0,text)

    def update(self, mouse_coords):
        x,y = mouse_coords
        if x < 0 or x > self.w or y >= -self.header_height or y <= -self.h:
            self.hovering = None
        else:
            self.hovering = len(self.entries) - (-y/self.entry_height)

    # figure out which entry will be executed upon mouse release
    def log_pending(self):
        self.pending = self.hovering

    def clear_pending(self):
        self.pending = None

    def execute_entry(self):
        if self.pending != None and self.hovering != None:
            f = self.entries[self.hovering][1]
            f()
