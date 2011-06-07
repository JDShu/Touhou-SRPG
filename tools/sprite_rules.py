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

class Sprite:
    def __init__(self, filename):
        self.filenmae
        self.actions = {}
        
    def set_frame(self, name, frame, dimensions):
        if name not in self.actions:
            self.actions[name] = []
    
        length = len(self.actions[name])
        while frame >= length:
            length += 1
            self.actions[name] += [None]
        self.actions[name][frame] = dimensions
