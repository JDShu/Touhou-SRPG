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

from tools.sprite_rules import *

OBJECTEVENT = pygame.locals.USEREVENT+4

# Todo: separate character/monster specific attributes from UI attributes.
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
        
        self.begin_turn_function = None
        self.end_turn_function = None
        
    def begin_turn(self):
        if self.begin_turn_function:
            self.begin_turn_function

    def end_turn(self):
        if self.end_turn_function:
            self.end_turn_function()

    #start moving one square, internal use only
    def start_moving(self, destination):
        self.moving = True
        self.dest = destination
        self.increments_moved = 1
        self.graphic.set_facing(convert(self.dest))

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

# Highlighted tiles object that displays all currently highlighted tiles when drawn.
class Highlight:
    def __init__(self, graphic):
        self.set = None
        self.graphic = MapGraphic(graphic, None, None, None)
        self.visible = False

    def on(self):
        self.visible = True

    def off(self):
        self.visible = False

    # new set of tiles
    def set_tiles(self, tiles):
        self.set = tiles

    def draw(self):
        if self.visible:
            for tile in self.set:
                self.graphic.pos = tile
                self.graphic.draw()
            
#signal that the map needs to be updated
def Update_Map(map_obj):
    e = pygame.event.Event(OBJECTEVENT, subtype=OBJECTEVENT, obj=map_obj)
    return e

def convert(dest):
    if dest == (1,0):
        return N
    elif dest == (-1,0):
        return S
    elif dest == (0,1):
        return W
    else:
        return E
