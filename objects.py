import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from math import *
import pickle
import sprite_rules

import level
import astar
import copy
import collections

TILE_DIMENSIONS = TILE_BASE, TILE_HEIGHT = level.TILE_DIMENSIONS
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
        # OpenGL < 2.0 hack
        #gluBuild2DMipmaps( GL_TEXTURE_2D, GL_RGBA, self.w, self.h, GL_RGBA, GL_UNSIGNED_BYTE, texture_data )
        # OpenGL >= 2.0
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

    def set_map_pos( self, x, y):
        base, height = TILE_DIMENSIONS
        width_offset, height_offset = TILE_OFFSETS
        Graphic.set_pos(self, -(x+y-0.5)*width_offset + base*x, (x-y+0.5)*height_offset + height*y)
        
class Tile( Graphic ):
    def __init__( self, x,y,a,base,height,width_offset, height_offset,filename,scale_factor = 1.0):
        Graphic.__init__( self, x,y,a,filename, scale_factor)
        self.base = base
        self.height = height
        self.width_offset = width_offset
        self.height_offset = height_offset
	
    def set_pos( self, x, y):
        Graphic.set_pos(self, -(x+y)*self.width_offset + self.base*x, (x-y)*self.height_offset + self.height*y)

class Animated:
    def __init__(self, x,y,sprite_name, scale_factor = 1.0):
        self.a = 1.0
        self.x, self.y = x,y
        self.set_sprite(sprite_name)
        self.current_action = "idle-s"
        self.current_frame_number = 0
        self.current_frame_dimensions = self.data.actions[self.current_action][self.current_frame_number]
        self.action = None
        self.w, self.h = self.current_frame_dimensions[2], self.current_frame_dimensions[3]
        self.w *= scale_factor
        self.h *= scale_factor
        self.scale_factor = scale_factor

    def set_action(self, action):
        self.current_action = action

    def set_pos(self, x, y):
        self.x, self.y =  x, y
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
            self.current_frame_number = 0
            self.current_frame_dimensions = self.data.actions[self.current_action][self.current_frame_number]
        self.w, self.h = self.current_frame_dimensions[2]*self.scale_factor, self.current_frame_dimensions[3]*self.scale_factor

    def Draw( self ):
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

class Actor( Animated ):
    def __init__( self, x,y,filename,scale_factor = 1.0):
        Animated.__init__( self, x,y,filename,scale_factor)
        self.idle = []
                
    #def update( self ):
    #    Animated.update()

    def set_pos(self, x, y):
        base, height = TILE_DIMENSIONS
        width_offset, height_offset = TILE_OFFSETS
        Animated.set_pos(self, -(x+y-0.5)*width_offset + base*x, (x-y+1)*height_offset + height*y)

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
        
        Animated.set_pos(self, self.x + distance*(up)*INC_UP, self.y + distance*(across)*INC_ACROSS)
                
class Character:
    READY, MOVING, MOVED = xrange(3)
    def __init__( self, spritesheet, across, down, portrait, stats = None, scale_factor = 1.0 ):
        self.actor = Actor(5,5,"reimu", scale_factor)
        #Actor( 0.0,0.0,1.0,across,down,spritesheet,scale_factor)
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
                self.actor.set_action("idle-s")
                self.direction = "left"
            elif across == 1:
                self.actor.set_action("idle-n")
                self.direction = "right"
            elif up == -1:
                self.actor.set_action("idle-e")
                self.direction = "down"
            elif up == 1:
                self.actor.set_action("idle-w")
                self.direction = "up"
                print "lol"
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
        self.previous_node = self.position
        
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
                    self.actor.set_action("idle-s")
                    self.direction = "left"
                elif across == 1:
                    self.actor.set_action("idle-n")
                    self.direction = "right"
                elif up == -1:
                    self.actor.set_action("idle-e")
                    self.direction = "down"
                elif up == 1:
                    self.actor.set_action("idle-w")
                    self.direction = "up"
                else:
                    self.direction = None
                pygame.event.post(pygame.event.Event(pygame.USEREVENT + 4))
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
    def find_accessible(self, level):
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
            temp = set()
            for t in accessible:
                if not (0 <= t[0] < level.w and 0 <= t[1] < level.h):
                    temp.add(t)
                elif level.map[t[0]][t[1]]:
                    temp.add(t)
                accessible = accessible.difference(temp)
            
        #temp = set()
        
        self.accessible = accessible
            
