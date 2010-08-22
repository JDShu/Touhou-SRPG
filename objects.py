import pygame
from OpenGL.GL import *
from OpenGL.GLU import *

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
    def __init__( self, x,y,a,base,height,top_offset,filename,scale_factor = 1.0):
        Graphic.__init__( self, x,y,a,filename, scale_factor)
        self.base = base
        self.height = height
        self.top_offset = top_offset
	
    def set_pos( self, x, y):
        Graphic.set_pos(self, y*self.top_offset + self.base*x, self.height*y)

class Animated( Graphic ):
    def __init__( self, x,y,a,across,down,filename,scale_factor = 1.0):
        Graphic.__init__( self, x,y,a,filename)
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
        Animated.__init__( self, x,y,a,across,down,filename,scale_factor = 1.0)
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

    def set_pos(self, x, y, tile_settings):
        base, height, offset = tile_settings
        Graphic.set_pos(self, y*offset + base*x, height*y)
