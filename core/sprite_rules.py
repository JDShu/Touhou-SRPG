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

N,S,E,W = range(4)

class Sprite:
    def __init__(self, filename):
        self.filename = filename
        self.frame = {}

    def new_action(self, action):
        direction = {}
        direction[N] = [None]
        direction[S] = [None]
        direction[E] = [None]
        direction[W] = [None]
        self.frame[action] = direction

    #TODO: don't clear it all out when called. Append instead.
    def set_number_of_frames(self, action, direction, number):
        #L = len(self.frame[action][direction])
        self.frame[action][direction] = [None]*number

    def set_frame(self, action, direction, frame_number, data):
        self.frame[action][direction][frame_number] = data
