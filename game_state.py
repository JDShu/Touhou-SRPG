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
