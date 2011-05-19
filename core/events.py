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

MOUSE = 1
TIME = 2

class Event():
    def __init__( self, category ):
        self.category = category        

class MouseEvent( Event ):
    def __init__( self, pygame_event ):
        Event.__init__( self, MOUSE )
        self.x, self.y = pygame.mouse.get_pos()
        self.l_click, self.m_click, self.r_click = pygame.mouse.get_pressed()
        self.s_up = False
        self.s_down = False
        
        if pygame_event.button == 4:
            self.s_up = True
        if pygame_event.button == 5:
            self.s_down = True

class TimeEvent( Event ):
    def __init__( self, time_type ):
        Event.__init__( self, TIME )
        self.time_type = time_type
