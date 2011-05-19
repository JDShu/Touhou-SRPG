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

import game_state

class MainLoop:
    def __init__( self, x, y, module ):
        pygame.display.init()
        pygame.display.set_caption("Touhou SRPG")
        self.width, self.height = x, y
        self.screen =  pygame.display.set_mode((self.width, self.height), pygame.OPENGL|pygame.DOUBLEBUF)
        glOrtho(0.0, self.width, 0.0, self.height,-1.0,1.0)
        glClearColor(0.0,0.0,0.0,0.0)    
        self.game_state = game_state.GameState(module)
                
    def process( self ):
        return self.game_state.process()
    
    def draw( self ):
        glClear(GL_COLOR_BUFFER_BIT)
        self.game_state.draw()
        pygame.display.flip()
