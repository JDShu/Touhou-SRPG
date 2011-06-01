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
from collections import deque

import misc.glFreeType as glFreeType

from core.graphics.graphic import Graphic, GraphicList

TITLE_HEIGHT = 40
MENU_BORDER = 10
ENTRY_HEIGHT, ENTRY_WIDTH = 40, 100

# Container class for everything UI
class UI:
    def __init__(self):
        self.elements = []

    def add(self, obj):
        self.elements += [obj]

    # gets called by the play session
    def draw(self):
        temp = GraphicList()
        temp.set_list(self.elements)
        return temp

class DeprecatedMenuBody( Graphic ):
    def __init__( self, filename,scale_factor = 1.0 ):
        h = MENU_BORDER*2 + TITLE_HEIGHT
        w = MENU_BORDER*2 + ENTRY_WIDTH
        Graphic.__init__( self, 0.8,filename,scale_factor,w,h)

    def add_entry( self ):
        self.h += ENTRY_HEIGHT
        self.setup_draw()

    def draw(self, x, y):
        y -= self.h
        Graphic.draw(self)


class DeprecatedMenuOptionGraphic:
    def __init__( self, place, idle, hover = None, clicked = None, scale_factor = 1.0 ): 

        h = ENTRY_HEIGHT
        w = ENTRY_WIDTH
    
        self.idle = Graphic(0.8,idle,scale_factor,w,h)
        
        if hover:
            self.hover = Graphic(0.8,hover,scale_factor,w,h)
        else:
            self.hover = None
        if clicked:
            self.clicked = Graphic(0.8,clicked,scale_factor,w,h)
        else:
            self.clicked = None

        self.h = ENTRY_HEIGHT
        self.w = ENTRY_WIDTH
        
        self.current = self.idle
        self.x, self.y = 0, 0
        self.place = place
        
    def determine_mode(self, mouse_pos, left_click):
        
        if self.x < mouse_pos[0] < self.x + self.w and self.y < mouse_pos[1] < self.y + self.h:
            if left_click and self.clicked:
                self.current = self.clicked
            elif self.hover:
                #print self.place, "hovering"
                self.current = self.hover
            return False
        else:
            self.current = self.idle
        return True

    def set_pos(self, x, y):
        self.x = x + MENU_BORDER
        self.y = y - TITLE_HEIGHT - MENU_BORDER - (self.place+1)*ENTRY_HEIGHT

    def draw(self):
        
        self.current.draw(self.x, self.y)
        #print self.place

class DeprecatedMenuEntry:
    def __init__( self, title, place, function, idle, hover = None, clicked = None, scale_factor = 1.0 ):
        self.gfx = "./content/gfx/gui/"

        self.title = title
        self.function = function
        self.mode = "idle"
        self.graphic = MenuOptionGraphic(place, self.gfx+idle, self.gfx+hover, self.gfx+clicked, scale_factor)
        self.place = place

    def execute( self, *args ):
        if self.function:
            return self.function(*args)
        else:
            print "No function implemented for this option"

    def draw(self):
        self.graphic.draw()
        
class DeprecatedMenu:
    
    def __init__( self, title):
        self.font = glFreeType.font_data( "./content/font/free_sans.ttf", 30 )
        self.title = title
        self.num_entries = 0
        self.body = MenuBody("./content/gfx/gui/menu_body.png")
        self.entries = []
        self.x, self.y = 0, 0
        self.visible = True
        self.screen_w = pygame.display.get_surface().get_width()
        
    def menu_on(self):
        self.visible = True
        
    def menu_off(self):
        self.visible = False

    def within_menu(self, x, y):
        return (self.x < x < self.x + self.body.w and self.y - self.body.h < y < self.y)
            
    def add_entry(self, entry):
        self.body.add_entry()
        self.entries += [entry]
        
    def process_click(self, *args):
        if self.visible:
            for entry in self.entries:
                if entry.graphic.current == entry.graphic.clicked:
                    entry.execute(*args)
                                        
        pass
            
    def update( self, mouse_pos, mouse_state ):
        for i, entry in enumerate(self.entries):
            entry.graphic.determine_mode(mouse_pos, mouse_state[0])
                                   
    def draw( self ):
        if self.visible:
            self.body.draw(self.x,self.y)
            for entry in self.entries:
        
                temp_x = self.x + MENU_BORDER
                temp_y = self.y - MENU_BORDER - TITLE_HEIGHT - (1+entry.place)*ENTRY_HEIGHT
            #print entry
                entry.draw()
                self.print_text(entry.title,temp_x,temp_y)
        #print "done"
            self.print_text(self.title, self.x + MENU_BORDER, self.y - TITLE_HEIGHT - MENU_BORDER)
        
    def print_text(self, text,x,y):
        glPushMatrix()
        glLoadIdentity()
        self.font.glPrint( x, y, text )
        glPopMatrix()

    def set_pos(self, x, y):
        self.x, self.y = x, y
        if y < self.body.h:
            self.y = y + self.body.h
        if x > self.screen_w - self.body.w:
            self.x = x - self.body.w
        for entry in self.entries:
            entry.graphic.set_pos(self.x, self.y)
        
        
class Menu:
    def __init__(self, title):
        self.title = title
        self.entries = []
        self.body_graphic = None
        self.entry_graphic = None
        self.entry_hover_graphic = None
        self.set_font("./content/font/free_sans.ttf", 12)
        self.header_height = 0
        self.entry_height = 0
        self.hovering = None

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

    def execute_entry(self):
        if self.pending != None and self.hovering != None:
            f = self.entries[self.hovering][1]
            f()
