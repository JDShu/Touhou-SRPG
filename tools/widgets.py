from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *
import pickle
import pygame

import objects
import glFreeType

def print_text(text,x,y,font):
    glPushMatrix()
    glLoadIdentity()
    font.glPrint( x, y, text, [ 1.0, 1.0, 0.0 ] )
    glPopMatrix()

class Widget:
    def __init__(self):
        pass
    
    def process_key(self, event):
        pass

    def process_click(self, mouse_x, mouse_y):
        pass

    def process_release(self, mouse_x, mouse_y):
        pass

    def draw(self):
        pass

class Input_Box(Widget):
    def __init__(self, x, y, modable = False):
        self.font = glFreeType.font_data( "free_sans.ttf", 20 )
        self.selected = False
        self.x, self.y = x, y
        self.modable = modable
        
    def draw(self):
        pass

    def process_click(self, mouse_x, mouse_y):
        mouse_y = 480 - mouse_y
        #print self, self.x, mouse_x, self.x + 100
        if self.x < mouse_x < self.x + 20 and self.y < mouse_y < self.y + 20:
            self.selected = True
        else:
            self.selected = False
        if self.selected:
            print self, "selected"
    
class Int_Box(Input_Box):
    def __init__(self, x, y, modable = False, default = "0"):
        
        Input_Box.__init__(self,x,y,modable)
        self.num = list(default)
        self.current = int(default)
        
    def process_key(self, event):
        key = event.key
        if self.selected and self.modable:
            if key == K_BACKSPACE:
                if self.num:
                    self.num.pop()
                else:
                    pass
            elif key == K_RETURN:
                self.selected = False
                self.current = self.number()
            elif 47 < key < 58:
                self.num.append(chr(key))
                #self.num = list(str(self.num))
                self.numberize()

    def process_click(self, mouse_x, mouse_y):
        Input_Box.process_click(self, mouse_x, mouse_y)
        self.current = self.number()

    def numberize(self):
        n = int("".join(self.num))
        self.num = list(str(n))

    def draw(self):
        print_text("".join(self.num), self.x, self.y, self.font)

    def number(self):
        return int("".join(self.num))

class Text_Box(Input_Box):
    def __init__(self, x, y, modable = False, default = "default"):
        Input_Box.__init__(self,x,y,modable)
        self.text_list = list(default)

    def process_key(self, event):
        key = event.key
        if self.selected and self.modable:
            if key == K_BACKSPACE:
                if self.text_list:
                    self.text_list.pop()
                else:
                    pass
            elif key == K_RETURN:
                self.selected = False
            elif key <= 127:
                if event.mod and KMOD_SHIFT:
                    key -= 32
                self.text_list.append(chr(key))

    def draw(self):
        print_text("".join(self.text_list), self.x, self.y, self.font)

    def text(self):
        return "".join(self.text_list)

class Button(Widget):
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

    def set_args(self, args):
        self.args = args
                 
    def draw(self):
        self.gfx_current.draw()

class Null_Widget(Widget):
    pass

class Selection_Box(Widget):
    def __init__(self, x, y, w, h, table, key):
        self.table = table
        self.key = key
        self.x, self.y = x,y
        self.w, self.h = w,h

    def set_dimensions(self, ox, oy, ow, oh):
        xs,ys,ws,hs = self.table[self.key].dimensions
        print self.table[self.key].dimensions
        x,y,w,h = ox.current, oy.current, ow.current, oh.current
        y = hs - y - h
        print "y =", y
        print x,y,w,h
        if xs <= x <= xs + ws and ys <= y <= ys + hs:
            print "set"
            self.x, self.y = x,y
            self.w, self.h = w,h

    def set_spritesheet(self, spritesheet):
        self.spritesheet = spritesheet

    def draw(self):
        glBegin(GL_LINE_LOOP)
        glVertex(self.x, self.y, 0)
        glVertex(self.x + self.w, self.y, 0)
        glVertex(self.x + self.w, self.y + self.h, 0)
        glVertex(self.x, self.y + self.h, 0)
        glEnd()        

class Animated:
    def __init__(self, x,y,sprite_name):
        self.a = 1.0
        self.x, self.y = x,y
        self.set_sprite(sprite_name)
        self.actions = sorted( self.data.actions.keys())
        self.action_index = 0
        self.current_action = self.actions[self.action_index]
        self.current_frame_number = 0
        self.current_frame_dimensions = self.data.actions[self.current_action][self.current_frame_number]
        self.action = None
        self.w, self.h = self.current_frame_dimensions[2], self.current_frame_dimensions[3]
        
        #self.image = None

    def set_sprite(self, sprite_name):
        try:
            self.data = pickle.load(open(sprite_name + ".spr"))
        except IOError:
            self.data = pickle.load(open(sprite_name + ".spr", "wb"))
            
        texture_surface = pygame.image.load(sprite_name + ".png")
        texture_data = pygame.image.tostring( texture_surface, "RGBA", 1 )
        
        self.image = glGenTextures(1)
        glBindTexture( GL_TEXTURE_2D, self.image )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST )
        self.tex_w, self.tex_h = texture_surface.get_width(), texture_surface.get_height()
        # OpenGL < 2.0 hack
        #gluBuild2DMipmaps( GL_TEXTURE_2D, GL_RGBA, self.w, self.h, GL_RGBA, GL_UNSIGNED_BYTE, texture_data )
        # OpenGL >= 2.0
        glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, self.tex_w, self.tex_h, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data )


    def update(self):
        self.current_frame_number += 1
        try:
            self.current_frame_dimensions = self.data.actions[self.current_action][self.current_frame_number]
        except IndexError:
            self.action_index += 1
            self.action_index = self.action_index % len(self.actions)
            self.current_action = self.actions[self.action_index]
            self.current_frame_number = 0
            self.current_frame_dimensions = self.data.actions[self.current_action][self.current_frame_number]
        self.w, self.h = self.current_frame_dimensions[2], self.current_frame_dimensions[3]

    def draw( self ):
        pix_x,pix_y,pix_w,pix_h = self.current_frame_dimensions
        x = float(pix_x)/float(self.tex_w)
        y = float(pix_y)/float(self.tex_h)
        w = float(pix_w)/float(self.tex_w)
        h = float(pix_h)/float(self.tex_h)
        y = 1.0 - y - h
        
        glPushMatrix()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        color = (1.0,1.0,1.0,1.0)
        glEnable( GL_TEXTURE_2D )
        glBindTexture( GL_TEXTURE_2D, self.image )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR )
        
        
        #draw
        glTranslatef(self.x,self.y,0.0)
        glColor4f(*color)
        glBegin(GL_QUADS)
        glTexCoord2f(x, y)
        glVertex(0.0,0.0,0.0)
        glTexCoord2f(x + w, y)
        glVertex(self.w,0.0,0.0)
        glTexCoord2f(x + w, y + h)
        glVertex(self.w,self.h,0.0)
        glTexCoord2f(x, y + h)
        glVertex(0.0,self.h,0.0)
        glEnd()
        glDisable( GL_TEXTURE_2D )
        glDisable( GL_BLEND)
        glPopMatrix()
        
