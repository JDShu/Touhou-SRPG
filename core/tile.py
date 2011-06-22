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

#Tile object for the ground in maps.
class Tile(Graphic):
    def __init__(self, image_file):
        Graphic.__init__(self, 1.0, image_file)

    def draw(self, x, y):
        """draw according to coordinate on grid"""
        glPushMatrix()
        Graphic.draw(self, x*self.w + (y-x)*self.x_offset, -y*self.h + (x+y)*self.y_offset)
        glPopMatrix()
