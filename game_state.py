import pygame

import play
import level

class Game_State:
    def __init__( self,w,h ):
        self.play = play.Play(w,h)

        test_level = level.Level(10,10) 
        self.play.load_level(test_level)
        
        self.current_mode = self.play
        self.map = None
        
    def process( self, current_mode ):
        #self.current_mode = self.play
        result = self.current_mode.process()
        return result
    
    def draw( self ):
        self.current_mode.draw()
        
            
