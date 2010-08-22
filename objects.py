import pygame
from OpenGL.GL import *
from OpenGL.GLU import *

class Graphic:
    def __init__( self, x,y,a,texture = None, scale_factor = 1.0):
        self.a = a
        self.x, self.y = x,y
        self.texture = texture
        print texture
        texture_surface = pygame.image.load(texture)
        texture_data = pygame.image.tostring( texture_surface, "RGBA", 1 )
            
        self.w = texture_surface.get_width()
        self.h = texture_surface.get_height()
        self.texture = glGenTextures(1)
        glBindTexture( GL_TEXTURE_2D, self.texture )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST )
        glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, self.w, self.h, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data )

        self.w = self.w*scale_factor
        self.h = self.h*scale_factor

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
    def __init__( self, x,y,a,base,height,top_offset,filename,scale_factor = 1.0):
        Graphic.__init__( self, x,y,a,filename, scale_factor = 1.0)
        self.base = base
        self.height = height
        self.top_offset = top_offset
	
    def set_pos( self, x, y):
        Graphic.set_pos(self, y*self.top_offset + self.base*x, self.height*y)
