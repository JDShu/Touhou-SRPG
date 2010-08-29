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
    font.glPrint( x, y, text, [ 1.0, 0.0, 0.0 ] )
    glPopMatrix()

class Menu_Body( Graphic ):
    def __init__( self, filename,scale_factor = 1.0 ):
        Graphic.__init__( self, 0.0,0.0,0.8,filename,scale_factor)
        self.h = MENU_BORDER*2 + TITLE_HEIGHT
        self.w = MENU_BORDER*2 + ENTRY_WIDTH

    def add_entry( self ):
        self.h += ENTRY_HEIGHT

    def set_pos(self, x,y):
        self.x = x
        self.y = y - self.h    

class Menu_Option_Graphic:
    def __init__( self, idle, hover = None, clicked = None, scale_factor = 1.0 ): #filename str arguments
        
        self.idle = Graphic(0.0,0.0,0.8,idle,scale_factor)
        self.idle.h = ENTRY_HEIGHT
        self.idle.w = ENTRY_WIDTH
        if hover:
            self.hover = Graphic(0.0,0.0,0.8,hover,scale_factor)
            self.hover.h = ENTRY_HEIGHT
            self.hover.w = ENTRY_WIDTH
        else:
            self.hover = None
        if clicked:
            self.clicked = Graphic(0.0,0.0,0.8,clicked,scale_factor)
            self.clicked.h = ENTRY_HEIGHT
            self.clicked.w = ENTRY_WIDTH
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

    def Draw( self ):
        self.current.Draw()
        
    def set_pos( self,x,y):
        temp_x = x + MENU_BORDER
        temp_y = y - MENU_BORDER - TITLE_HEIGHT
        self.idle.set_pos(temp_x,temp_y)
        if self.hover:
            self.hover.set_pos(temp_x,temp_y)
        if self.clicked:
            self.clicked.set_pos(temp_x,temp_y)
    
class Menu_Entry:
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
    def __init__( self, title ):
        self.font = glFreeType.font_data( "free_sans.ttf", 30 )
        self.title = title
        self.num_entries = 0
        self.body = Menu_Body("menu_body.png")
        self.option = Menu_Option_Graphic("menu_option.png", "menu_option_hover.png")
        self.entries = []
        self.x, self.y = 0, 0
        self.visible = False
        self.screen_w = pygame.display.get_surface().get_width()
        
    def toggle(self):
        self.visible = not self.visible
        
    def add_entry(self, entry):
        self.body.add_entry()
        self.entries += [entry]

    def process_click(self, *args):
        if self.visible:
            for entry in self.entries:
                if entry.graphic.current == entry.graphic.clicked:
                    entry.execute(*args)
            self.visible = False
        
    def update( self, mouse_pos, left_click ):
        for i, entry in enumerate(self.entries):
            entry.set_pos(self.x, self.y, i)
            entry.graphic.determine_mode(mouse_pos, left_click)
                           
    def Draw( self ):
        if self.visible:
            self.body.Draw()
            for i, entry in enumerate(self.entries):
                temp_x = self.x + MENU_BORDER
                temp_y = self.y - MENU_BORDER - TITLE_HEIGHT - (1+i)*ENTRY_HEIGHT
                entry.graphic.current.Draw()
                
                print_text(entry.title,temp_x,temp_y,self.font)
            print_text(self.title,self.x + MENU_BORDER,self.y - TITLE_HEIGHT - MENU_BORDER,self.font)
            
    def set_pos(self, x, y):
        self.x, self.y = x, y
        if y < self.body.h:
            self.y = y + self.body.h
        if x > self.screen_w - self.body.w:
            self.x = x - self.body.w
        self.body.set_pos(self.x, self.y)
        
            

