import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from math import *

import level

TILE_DIMENSIONS = level.TILE_DIMENSIONS
TILE_OFFSETS = level.TILE_OFFSETS
ratio = sqrt(pow(TILE_DIMENSIONS[0],2) + pow(TILE_DIMENSIONS[1],2))
INC_UP = TILE_DIMENSIONS[0]/ratio
INC_ACROSS = TILE_DIMENSIONS[1]/ratio

def square_to_screen(x,y):
    base, height = TILE_DIMENSIONS
    width_offset, height_offset = TILE_OFFSETS
    return -(x+y-0.5)*width_offset + base*x, (x-y+1)*height_offset + height*y


class Graphic:
    def __init__( self, x,y,a,texture = None, scale_factor = 1.0):
        self.a = a
        self.x, self.y = x,y
        self.texture = texture
        texture_surface = pygame.image.load(texture)
        texture_data = pygame.image.tostring( texture_surface, "RGBA", 1 )
            
        self.w = texture_surface.get_width()
        self.h = texture_surface.get_height()
        self.texture = glGenTextures(1)
        glBindTexture( GL_TEXTURE_2D, self.texture )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST )
        glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, self.w, self.h, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data )

        self.w *= scale_factor
        self.h *= scale_factor

    def set_pos(self, x,y):
        self.x = x
        self.y = y
        #print "position set to", x, y
        
    def Draw( self ):
        #set up
        glPushMatrix()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        color = (1.0,1.0,1.0,self.a)
        glEnable( GL_TEXTURE_2D )
        glBindTexture( GL_TEXTURE_2D, self.texture )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR )

        #draw
        glTranslatef(self.x,self.y,0.0)
        glColor4f(*color)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex(0.0,0.0,0.0)
        glTexCoord2f(1.0, 0.0)
        glVertex(self.w,0.0,0.0)
        glTexCoord2f(1.0, 1.0)
        glVertex(self.w,self.h,0.0)
        glTexCoord2f(0.0, 1.0)
        glVertex(0.0,self.h,0.0)
        glEnd()
        glDisable( GL_TEXTURE_2D )
        glDisable( GL_BLEND)
        glPopMatrix()

class Tile( Graphic ):
    def __init__( self, x,y,a,base,height,width_offset, height_offset,filename,scale_factor = 1.0):
        Graphic.__init__( self, x,y,a,filename, scale_factor)
        self.base = base
        self.height = height
        self.width_offset = width_offset
        self.height_offset = height_offset
	
    def set_pos( self, x, y):
        Graphic.set_pos(self, -(x+y)*self.width_offset + self.base*x, (x-y)*self.height_offset + self.height*y)

class Animated( Graphic ):
    def __init__( self, x,y,a,across,down,filename,scale_factor = 1.0):
        Graphic.__init__( self, x,y,a,filename,scale_factor)
        self.across = across
        self.down = down
        self.sprite_width = 1.0/across
        self.sprite_height = 1.0/down
        self.current_frame = (0,0)
        self.w /= across
        self.h /= down
        
    def Draw( self ):

        tex_x = self.current_frame[0]*self.sprite_width
        tex_x2 = tex_x + self.sprite_width
        tex_y = self.current_frame[1]*self.sprite_height
        tex_y2 = tex_y + self.sprite_height
        
        glPushMatrix()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        color = (1.0,1.0,1.0,self.a)
        glEnable( GL_TEXTURE_2D )
        glBindTexture( GL_TEXTURE_2D, self.texture )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR )

        #draw
        glTranslatef(self.x,self.y,0.0)
        glColor4f(*color)
        glBegin(GL_QUADS)
        glTexCoord2f(tex_x, tex_y)
        glVertex(0.0,0.0,0.0)
        glTexCoord2f(tex_x2, tex_y)
        glVertex(self.w,0.0,0.0)
        glTexCoord2f(tex_x2, tex_y2)
        glVertex(self.w,self.h,0.0)
        glTexCoord2f(tex_x, tex_y2)
        glVertex(0.0,self.h,0.0)
        glEnd()
        glDisable( GL_TEXTURE_2D )
        glDisable( GL_BLEND)
        glPopMatrix()

class Actor( Animated ):
    def __init__( self, x,y,a,across,down,filename,scale_factor = 1.0):
        Animated.__init__( self, x,y,a,across,down,filename,scale_factor)
        self.idle = []
        for i in xrange(self.across):
            self.idle += [(i,0)]
        self.current_routine = self.idle
        self.frame_index = 0
        
    def update( self ):
        self.frame_index += 1
        if self.frame_index == self.across:
            self.frame_index = 0
        self.current_frame = self.current_routine[self.frame_index] 

    def set_pos(self, x, y):
        base, height = TILE_DIMENSIONS
        width_offset, height_offset = TILE_OFFSETS
        Graphic.set_pos(self, -(x+y-0.5)*width_offset + base*x, (x-y+1)*height_offset + height*y)

    def step(self,up,across,speed = 5.0):
        Graphic.set_pos(self, self.x +speed*(up)*INC_UP, self.y + speed*(across)*INC_ACROSS)
        
class Character:
    def __init__( self, spritesheet, across, down, portrait, stats = None, scale_factor = 1.0 ):
        self.actor = Actor( 0.0,0.0,1.0,across,down,spritesheet,scale_factor)
        self.portrait = Graphic( 0.0,0.0,1.0,portrait, 2*scale_factor)        
        self.position = self.x, self.y = 0,0
        self.moving = False
        
    #in tile coordinates
    def set_pos(self, x ,y):
        self.actor.set_pos(x,y)
        self.position = self.x, self.y = x,y

    def move_to( self, x, y ):
        self.moving = True
        self.destination = (x,y)
        base, height = TILE_DIMENSIONS
        width_offset, height_offset = TILE_OFFSETS
        self.map_dest = square_to_screen(x,y)
        
#self.set_pos(x,y)

    def step( self,up,across,speed, destination):
        #print destination[0], self.actor.x
        temp_x, temp_y = square_to_screen(*destination)
        if abs(temp_x - self.actor.x) > speed:
            self.actor.step(up,across,speed)
        else:
            self.set_pos(*destination)
            #print "Arrived: ", self.x, self.y
            
    def pos_update( self ):
        if self.moving:  
            #print self.destination, (self.x,self.y)
            if self.destination[0] < self.x:
                self.step(-1,-1,5.0,(self.x - 1, self.y))
            elif self.destination[0] > self.x:
                self.step(1,1,5.0,(self.x + 1, self.y))
            elif self.destination[1] < self.y:
                self.step(1,-1,5.0,(self.x, self.y - 1))
            elif self.destination[1] > self.y:
                self.step(-1,1,5.0,(self.x, self.y + 1))
            else:
                self.moving = False
    def anim_update(self):
        self.actor.update()
