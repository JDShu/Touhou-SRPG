import pygame

MOUSE = 1
TIME = 2

class Event():
    def __init__( self, category ):
        self.category = category        

class MouseEvent( Event ):
    def __init__( self, pygame_event ):
        Event.__init__( self, MOUSE )
        self.x, self.y = pygame.mouse.get_pos()
        self.l_click, self.m_click, self.r_click = pygame.mouse.get_pressed()
        self.s_up = False
        self.s_down = False
        
        if pygame_event.button == 4:
            self.s_up = True
        if pygame_event.button == 5:
            self.s_down = True

class TimeEvent( Event ):
    def __init__( self, time_type ):
        Event.__init__( self, TIME )
        self.time_type = time_type
