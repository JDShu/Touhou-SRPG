import pygame
from OpenGL.GL import *

import game_state

class Main_Loop:
    def __init__( self, x, y ):
        pygame.display.init()
        pygame.display.set_caption("Touhou SRPG")
        self.width, self.height = x, y
        self.screen =  pygame.display.set_mode((self.width, self.height), pygame.OPENGL)
        glOrtho(0.0, self.width, 0.0, self.height,-1.0,1.0)
        glClearColor(0.0,0.0,0.0,0.0)    
        self.current_mode = None
        self.game_state = game_state.Game_State(x,y)
        pygame.time.set_timer(pygame.USEREVENT+1, 200)
        
    def process( self ):
        self.current_mode = self.game_state.process( self.current_mode )
        return self.current_mode
    
    def draw( self ):
        glClear(GL_COLOR_BUFFER_BIT)
        self.game_state.draw()
        pygame.display.flip()
