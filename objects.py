import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from math import *

import level
import astar
import copy
import collections

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
    def __init__( self, x,y,a,texture = None, scale_factor = 1.0, w = None, h = None):
        self.a = a
        self.x, self.y = 0,0#x,y
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

        if w:
            self.w = w
        if h:
            self.h = h
        
        self.w *= scale_factor
        self.h *= scale_factor
        
        #pregenerate render code
        self.draw_list = glGenLists(2)
        self.draw_list_2 = self.draw_list + 1 
        self.setup_draw()
        
    def set_pos(self, x,y):
        self.x = x
        self.y = y
        #print "position set to", x, y

    def setup_draw( self ):
        
        glNewList(self.draw_list, GL_COMPILE)
        glPushMatrix()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        color = (1.0,1.0,1.0,self.a)
        glEnable( GL_TEXTURE_2D )
        glBindTexture( GL_TEXTURE_2D, self.texture )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR )
        glEndList()

        glNewList(self.draw_list_2,GL_COMPILE)
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
        
        glEndList()
        
    def Draw( self ):
        #set up
        glCallList(self.draw_list)
        glTranslatef(self.x,self.y,0.0)
        glCallList(self.draw_list_2)

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

    #def step(self,up,across,speed = 5.0):
    #    Graphic.set_pos(self, self.x +speed*(up)*INC_UP, self.y + speed*(across)*INC_ACROSS)
    # return screen coordinates after moving actor by "distance"
    def move( self, distance, direction ):
        if direction == "up":
            up = -1
            across = 1
        elif direction == "down":
            up = 1
            across = -1
        elif direction == "left":
            up = -1
            across = -1
        else:
            up = 1
            across = 1
        
        Graphic.set_pos(self, self.x + distance*(up)*INC_UP, self.y + distance*(across)*INC_ACROSS)
                
class Character:
    READY, MOVING, MOVED = xrange(3)
    def __init__( self, spritesheet, across, down, portrait, stats = None, scale_factor = 1.0 ):
        self.actor = Actor( 0.0,0.0,1.0,across,down,spritesheet,scale_factor)
        self.portrait = Graphic( 0.0,0.0,1.0,portrait, 2*scale_factor)        
        self.position = self.x, self.y = 0,0
        self.moving = self.READY
        self.before_position = self.position
        self.stats = stats
        #movement variables
        self.path = collections.deque()
        self.next_node = None
        self.next_node_coordinate = None
        self.direction = None
        self.accessible = []
        
    #in tile coordinates
    def set_pos(self, x ,y):
        self.actor.set_pos(x,y)
        self.position = self.x, self.y = x,y

    #takes the map and the destination as input and returns a list of map coordinates leading to destination
    def move_to( self, level, destination ):
        if destination in self.accessible:
            self.before_position = self.position
            temp_grid = astar.Grid(level)
            path = astar.Path(temp_grid, self.position, [(int(destination[0]),int(destination[1]))])
            self.path = collections.deque()
            for c in path.path:
                self.path.appendleft(c)
            #print self.path
            self.next_node = self.path.popleft()
            self.next_node_coordinate = square_to_screen(*self.next_node)
            #print self.next_node, self.position
            #calculate direction
            across = self.next_node[0] - self.position[0]
            up = self.next_node[1] - self.position[1]
            if across == -1:
                self.direction = "left"
            elif across == 1:
                self.direction = "right"
            elif up == -1:
                self.direction = "down"
            elif up == 1:
                self.direction = "up"
            else:
                self.direction = None
        
#move to next coordinate in path    
    def move( self ):
        if self.next_node and self.position != self.next_node:
            #move according to direction
            self.move_update()

    #the actual function that updates the position, if it arrives at the node, it snaps to position
    def move_update( self ):
        x, y = self.position
        self.actor.move(10.0, self.direction)
        #check arrived condition
        if abs(self.actor.x - self.next_node_coordinate[0]) < 10*INC_UP:
            self.set_pos(*self.next_node)
            self.position = self.next_node
            if self.path:
                self.next_node = self.path.popleft()
                self.next_node_coordinate = square_to_screen(*self.next_node)
                #calculate which direction
                across = self.next_node[0] - self.position[0]
                up = self.next_node[1] - self.position[1]
                if across == -1:
                    self.direction = "left"
                elif across == 1:
                    self.direction = "right"
                elif up == -1:
                    self.direction = "down"
                elif up == 1:
                    self.direction = "up"
                else:
                    self.direction = None
            else:
                pygame.event.post(pygame.event.Event(pygame.USEREVENT + 3))
                direction = None
                self.moving = self.MOVED
        
    def revert(self):
        self.position = self.before_position
        self.set_pos(*self.position)
        self.moving = self.READY
        self.direction = None
        self.next_node = self.position
        
    def confirm(self):
        self.before_position = self.position
        self.moving = self.READY
        
    def anim_update(self):
        self.actor.update()

    #create a list of map coordinates that the character is allowed to move to
    def find_accessible(self):
        accessible = set()
        accessible.add(self.position)
        for i in xrange(self.stats.speed):
            temp = set()
            for c in accessible:
                temp.add((c[0],c[1]-1))
                temp.add((c[0],c[1]+1))
                temp.add((c[0]-1,c[1]))
                temp.add((c[0]+1,c[1]))
            accessible = accessible.union(temp)
        self.accessible = accessible
            
