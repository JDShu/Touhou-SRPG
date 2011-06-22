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
    def __init__(self):
        self.frames = {}

    def new_action(self, action_name, num_frames):
        action = {}
        action[N] = [None]*num_frames
        action[S] = [None]*num_frames
        action[E] = [None]*num_frames
        action[W] = [None]*num_frames
        self.frames[action_name] = action

    def add_frame(self,action, facing):
        self.frames[action][facing] += [None]

    def remove_frame(self,action,facing,frame):
        self.frames[action][facing].pop(frame)

    def set_frame(self, action, facing, frame, data):
        self.frames[action][facing][frame] = data

class FrameData:
    def __init__(self):
        self.x, self.y = None, None
        self.w, self.h = None, None

    def set_pos(self, pos):
        self.x, self.y = pos

    def set_dim(self, dim):
        self.w, self.h = dim

    def get_tuple(self):
        return self.x, self.y, self.w, self.h
