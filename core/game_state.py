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
import play


class GameState:
    """determines what session to run for the given module at a given time"""
    def __init__(self, module):
        self.module = module()

        #global variables
        self.level = None
        self.map = self.test_map()

        #various sessions
        self.main_menu = None
        self.load_game = None
        self.play = play.Play(self.module, self.map)
        
        #temporarily test play mode
        self.current_mode = self.play


    def process(self):
        return self.current_mode.process()
    
    def draw(self):
        self.current_mode.draw()
        
    #temporary map for testing before load map possible
    def test_map(self):
        test_map = self.module.map((10,10))
        return test_map
