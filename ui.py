import pygame
import glFreeType
from OpenGL.GL import *

from objects import *

TITLE_HEIGHT = 40
MENU_BORDER = 10
ENTRY_HEIGHT, ENTRY_WIDTH = 40, 100

def print_text(text,x,y,font):
    glPushMatrix()
    glLoadIdentity()
    font.glPrint( x, y, text, [ 1.0, 1.0, 0.0 ] )
    glPopMatrix()

class Menu_Body( Graphic ):
    def __init__( self, filename,scale_factor = 1.0 ):
        h = MENU_BORDER*2 + TITLE_HEIGHT
        w = MENU_BORDER*2 + ENTRY_WIDTH
        Graphic.__init__( self, 0.8,filename,scale_factor,w,h)

    def add_entry( self ):
        self.h += ENTRY_HEIGHT
        self.setup_draw()

    def set_pos(self, x,y):
        self.x = x
        self.y = y - self.h    
        
class Menu_Option_Graphic:
    def __init__( self, idle, hover = None, clicked = None, scale_factor = 1.0 ): #filename str arguments

        h = ENTRY_HEIGHT
        w = ENTRY_WIDTH
    
        self.idle = Graphic(0.8,idle,scale_factor,w,h)
        
        if hover:
            self.hover = Graphic(0.8,hover,scale_factor,w,h)
        else:
            self.hover = None
        if clicked:
            self.clicked = Graphic(0.8,clicked,scale_factor,w,h)
        else:
            self.clicked = None

        self.h = ENTRY_HEIGHT
        self.w = ENTRY_WIDTH
        
        self.current = self.idle
        
    def determine_mode(self, mouse_pos, left_click):
        x, y = self.current.x, self.current.y
        if x < mouse_pos[0] < x + self.w and y < mouse_pos[1] < y + self.h:
            if left_click and self.clicked:
                self.current = self.clicked
            elif self.hover:
                self.current = self.hover
            return False
        else:
            self.current = self.idle
        return True

    def draw( self ):
        self.current.draw()
        
    def set_pos( self,x,y):
        temp_x = x + MENU_BORDER
        temp_y = y - MENU_BORDER - TITLE_HEIGHT
        self.idle.set_pos(temp_x,temp_y)
        if self.hover:
            self.hover.set_pos(temp_x,temp_y)
        if self.clicked:
            self.clicked.set_pos(temp_x,temp_y)
    
class MenuEntry:
    def __init__( self, title, function, idle, hover = None, clicked = None, scale_factor = 1.0 ):
        self.title = title
        self.function = function
        self.mode = "idle"
        self.graphic = Menu_Option_Graphic(idle,hover,clicked,scale_factor)
        
    def execute( self, *args ):
        return self.function(*args)

    def set_pos(self,x,y,i):
        self.graphic.set_pos( x,y - (1 + i)*self.graphic.h )
        
        
class Menu:
    
    def __init__( self, title):
        self.font = glFreeType.font_data( "free_sans.ttf", 30 )
        self.title = title
        self.num_entries = 0
        self.body = Menu_Body("menu_body.png")
        self.option = Menu_Option_Graphic("menu_option.png", "menu_option_hover.png")
        self.entries = []
        self.x, self.y = 0, 0
        self.visible = False
        self.screen_w = pygame.display.get_surface().get_width()
        
    def add_entry(self, entry):
        self.body.add_entry()
        self.entries += [entry]

    def process_click(self, *args):
        #if self.visible:
         #   for entry in self.entries:
         #       if entry.graphic.current == entry.graphic.clicked:
         #           entry.execute(*args)
         #           self.visible = False
        pass
            
    def update( self, mouse_pos, left_click ):
        for i, entry in enumerate(self.entries):
            entry.set_pos(self.x, self.y, i)
            entry.graphic.determine_mode(mouse_pos, left_click)
                                   
    def draw( self ):

        self.body.draw(self.x,self.y - TITLE_HEIGHT - 2*MENU_BORDER)
        self.print_text(self.title, self.x + MENU_BORDER, self.y - TITLE_HEIGHT - MENU_BORDER)
        self.print_text(self.title, 0,0)
        for i, entry in enumerate(self.entries):
            temp_x = self.x + MENU_BORDER
            temp_y = self.y - MENU_BORDER - TITLE_HEIGHT - (1+i)*ENTRY_HEIGHT
            entry.graphic.current.draw()
            print_text(entry.title,temp_x,temp_y,self.font)
        

    def print_text(self, text,x,y):
        glPushMatrix()
        #print "printing test"
        #glLoadIdentity()
        self.font.glPrint( x, y, text )
        glPopMatrix()
        
    def set_pos(self, x, y):
        print x, y
        self.x, self.y = x, y
        if y < self.body.h:
            self.y = y + self.body.h
        if x > self.screen_w - self.body.w:
            self.x = x - self.body.w
        self.body.set_pos(self.x, self.y)
        
        
