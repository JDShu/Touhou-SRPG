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
