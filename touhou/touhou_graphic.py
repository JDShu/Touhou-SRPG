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

from core.graphics.graphic import GraphicPositioned

OBJECTEVENT = pygame.locals.USEREVENT+4

class MapGraphic(GraphicPositioned):
    TILE_OFFSET = (45.0,30.0)
    TILE_DIMENSIONS = (90.0,60.0)
    TILE_DATA = (TILE_OFFSET, TILE_DIMENSIONS)
    
    def __init__(self, graphic, pos, name, details=None):
        GraphicPositioned.__init__(self, graphic, (0,0))
        self.pos = pos
        self.graphic = graphic
        self.name = name
        self.details = details

        self.moving = False
        self.dest = None
        self.increments = 10
        self.increments_moved = 1
        self.pixel_increment = self.TILE_OFFSET[0]/self.increments, self.TILE_OFFSET[1]/self.increments
        self.path = None
        self.visible = True
        

    #start moving one square, internal use only
    def start_moving(self, destination):
        self.moving = True
        self.dest = destination
        self.increments_moved = 1

    #follow path of coordinates
    def move_path(self, path):
        self.path = path
        direction = (self.path[0][0]-self.pos[0], self.path[0][1]-self.pos[1])
        self.signs = self.calculate_signs(*direction)
        self.start_moving(direction)

    def update(self, e):
        if self.moving:
            if self.increments_moved >= self.increments:
                self.moving = False
                self.pos = (self.pos[0] + self.dest[0], self.pos[1] + self.dest[1])
                self.path = self.path[1:]
                self.destination = None
                self.increments_moved = 1
                if self.path:
                    direction = (self.path[0][0]-self.pos[0], self.path[0][1]-self.pos[1])
                    self.signs = self.calculate_signs(*direction)
                    self.start_moving(direction)
                pygame.event.post(Update_Map(self))
                                
            else:
                self.increments_moved += 1
        
    #calculate draw coordinate signs from unit coordinate
    def calculate_signs(self,x,y):
        if x == 1:
            return (1,1)
        elif x == -1:
            return (-1,-1)
        elif y == -1:
            return (1,-1)
        else:
            return (-1,1)
        
    def draw(self):
        if self.visible:
            glPushMatrix()
            tile_x = self.pos[0]*self.TILE_OFFSET[0] - self.pos[1]*self.TILE_OFFSET[0]
            tile_y = self.pos[0]*self.TILE_OFFSET[1] + self.pos[1]*self.TILE_OFFSET[1]
            glTranslate(tile_x, tile_y, 0.0)
            if self.moving:
            #print self.signs
                fraction = float(self.increments_moved)/self.increments
                sx, sy = self.signs
                inc_x = sx*self.TILE_OFFSET[0]*fraction
                inc_y = sy*self.TILE_OFFSET[1]*fraction
                glTranslate(inc_x, inc_y, 0.0)
            
            self.graphic.draw()
            glPopMatrix()

# Class that contains details of objects on the scenario map.
class MapObject:
    def __init__(self, name):
        self.name = name
        self.type = None
        
class Character(MapObject):
    def __init__(self, name, speed=1):
        MapObject.__init__(self, name)
        self.speed = speed

    def set_speed(self, speed):
        self.speed = speed

#signal that the map needs to be updated
def Update_Map(map_obj):
    e = pygame.event.Event(OBJECTEVENT, subtype=OBJECTEVENT, obj=map_obj)
    #print map_obj.pos
    return e
