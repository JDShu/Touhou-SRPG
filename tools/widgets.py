from OpenGL.GL import *
from pygame.locals import *

import objects
import glFreeType

def print_text(text,x,y,font):
    glPushMatrix()
    glLoadIdentity()
    font.glPrint( x, y, text, [ 1.0, 1.0, 0.0 ] )
    glPopMatrix()

class Text_Box:
    def __init__(self, x, y, title, modable = False, default = "default"):
        self.font = glFreeType.font_data( "free_sans.ttf", 20 )
        self.title = title
        self.text = list(default)
        self.selected = False
        self.x, self.y = x, y
        self.modable = modable

    def draw(self):
        print_text("".join(self.text), self.x, self.y, self.font)

    def process_click(self, mouse_x, mouse_y):
        mouse_y = 480 - mouse_y
        if self.x < mouse_x < self.x + 100 and self.y < mouse_y < self.y + 20:
            self.selected = True
        else:
            self.selected = False

    def process_key(self, key):
        if self.selected and self.modable:
            if key == K_BACKSPACE:
                if self.text:
                    self.text.pop()
                else:
                    pass
            elif key == K_RETURN:
                self.selected = False
            elif key <= 127:
                self.text.append(chr(key))

    def process_release( self, mouse_x, mouse_y ):
        pass

class Button:
    def __init__(self, x,y,gfx_idle, gfx_pressed, function, args = ()):
        self.gfx_idle = objects.Graphic(x,y,1.0,gfx_idle)
        self.gfx_pressed = objects.Graphic(x,y,1.0,gfx_pressed)
        self.x, self.y = self.gfx_idle.x, self.gfx_idle.y
        self.w, self.h = self.gfx_idle.w, self.gfx_idle.h
        self.gfx_current = self.gfx_idle
        self.function = function
        self.args = args
        
    def process_click(self, mouse_x, mouse_y):
        mouse_y = 480 - mouse_y
        if self.x < mouse_x < self.x + self.w and self.y < mouse_y < self.y + self.h:
            self.gfx_current = self.gfx_pressed
            
    def process_release(self, mouse_x, mouse_y):
        mouse_y = 480 - mouse_y
        if self.x < mouse_x < self.x + self.w and self.y < mouse_y < self.y + self.h:
            self.function(*self.args)
        self.gfx_current = self.gfx_idle

    def process_key(self, key):
        pass

    def set_args(self, args):
        self.args = args
                 
    def draw(self):
        self.gfx_current.draw()
