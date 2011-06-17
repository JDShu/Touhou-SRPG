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
from tools.sprite_rules import *

class Animated:
    def __init__(self, spritesheet, datafile=None):

        self.spritesheet = Graphic(spritesheet)
        self.current_frame = 0
        self.action = None
        self.facing = None

        if datafile:
            self.use_datafile(datafile)
            self.set_action("idle")
            self.set_facing(S)
        else:
            self.data = Sprite()
            self.current_frame_data = (0,0,100,150)
        
    def set_data(self, data):
        self.data = data

    def use_datafile(self, datafile):
        F = open(datafile, 'r')
        self.data = pickle.load(F)

    def set_action(self, action):
        self.action = action
        self.current_frame = 0
        self.get_current_dimensions()

    def set_facing(self, facing):
        self.facing = facing
        self.get_current_dimensions()

    def set_current_frame(self, frame):
        self.current_frame = frame
        self.get_current_dimensions()

    def update(self, event=None):
        if self.action:
            self.current_frame += 1
            if len(self.data.frames[self.action][self.facing]) <= self.current_frame:
                self.current_frame = 0
            if self.data.frames[self.action][self.facing][self.current_frame]:
                self.get_current_dimensions()

    def get_current_dimensions(self):
        if self.action and self.facing != None and self.current_frame != None:
            framedata = self.data.frames[self.action][self.facing][self.current_frame]
            self.current_frame_data = framedata.get_tuple()
            
    def draw(self):
        self.spritesheet.draw_section(self.current_frame_data)
