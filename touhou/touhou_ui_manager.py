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

from core.graphics.graphic import Graphic, GraphicList

TITLE_HEIGHT = 40
MENU_BORDER = 10
ENTRY_HEIGHT, ENTRY_WIDTH = 40, 100

# Container class for everything UI
# under_elements: displayed underneat map sprites
# top_elements: displayed on the top
class UI:
    def __init__(self):
        self.top_elements = []
        self.under_elements = []

    def add(self, obj):
        self.top_elements += [obj]

    def add_under(self, obj):
        self.under_elements += [obj]

    # gets called by the play session
    def draw(self):
        temp = GraphicList()
        temp.set_list(self.top_elements)
        return temp

    def draw_under(self):
        temp = GraphicList()
        temp.set_list(self.under_elements)
        return temp

