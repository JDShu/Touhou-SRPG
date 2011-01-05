import level
import objects
import pygame
from OpenGL.GL import *
from math import *

class Module:
    """
    Stores classes that define the module:
    map: map of objects in a sigle play session
    play: play session state
    """
    def __init__(self):
        self.map = TouhouMap
        self.play = TouhouPlay

class TouhouMap:
    """The current map and what is on it"""
    def __init__(self,dimensions):
        """
        grid: w by h grid that stores where everything is
        actors: All active characters in the play session
        tileset: What to draw with OpenGL
        """
        self.w, self.h = dimensions
        #tiles dimensions and offsets
        self.dimensions = (90,60)
        self.offsets = (45,30)

        self.grid = []
        for y in xrange(self.h):
            temp = []
            for x in xrange(self.w):
                temp += [None]
            self.grid += [temp]
        self.tileset = self.temp_tileset()
        self.actors = []

    def draw(self,offsets):
        """Draws everything that is on the board."""
        glTranslatef(*offsets)
        self.draw_floor()
        self.draw_objects()
        
    def draw_floor(self):
        """Draw the board."""
        
        for x in range(self.w):
            for y in range(self.h):
                self.tileset["ground"].draw_grid(x,y,self.dimensions, self.offsets)
                
    def draw_objects(self):
        """Draw Active and Inactive objects"""
        
        for x in range(self.w):
            for y in range(self.h):
                if self.grid[x][y]:
                    self.grid[x][y].draw_grid(x,y,self.dimensions, self.offsets)

    def temp_tileset(self):
        """Temporary tileset and objects to place on map"""
        tileset = {}
        tileset["ground"] = objects.Graphic(1.0,"grass.png")
        tileset["obstacle"] = objects.Graphic(1.0,"tree.png")
        self.grid[3][3] = tileset["obstacle"]
        self.tile_w = sqrt(pow(self.offsets[0],2) + pow(self.offsets[1],2))
        return tileset

    def insert(self,instance,position):
        self.grid[position[0]][position[1]] = instance

    def process_click(self, mouse_coords, offsets):
        mouse_x, mouse_y = mouse_coords
        
        mouse_x -= offsets[0]
        mouse_y -= offsets[1] + self.offsets[1]
        
        
        theta1 = atan(float(self.offsets[0])/float(self.offsets[1]))
        theta2 = atan(float(self.offsets[1])/float(self.offsets[0]))
        x = mouse_x*cos(theta1) + mouse_y*sin(theta1)
        
        y = mouse_x*sin(theta2) - mouse_y*cos(theta2)
        
        max_x = self.tile_w*(self.w-1)
        max_y = self.tile_w*(self.h-1)
        if 0 < x < max_x and 0 < y < max_y:
            cell_x, cell_y = int(floor((x/max_x)*self.w)), int(floor((y/max_y)*self.h))
            if self.grid[cell_x][cell_y]:
                self.grid[cell_x][cell_y].process_click()



class TouhouPlay:
    """The state of a Touhou play session at any given moment"""
    FRAMEUPDATE = pygame.USEREVENT + 1

    def __init__(self, touhou_map):
        """ 
        selectable: Characters that can be clicked on at a given moment
        menu: Menu options available if it is called up
        map: what is currently on the map
        
        """
        self.active = []
        self.menu = {}
        self.map = touhou_map
        self.offsets = [0,0,0]

        
        self.test_objects()

        #Custom Events for Touhou Module
        pygame.time.set_timer(self.FRAMEUPDATE,300)
        
    def test_objects(self):
        reimu = objects.Actor(15,15,"reimu")
        position = (4,4)
        self.active += [(reimu,position)] 
        self.map.insert(reimu,position)

    def update(self):
        for a in self.active:
            a[0].update()

    def process_click(self, mouse_coords, mouse_state):
        """ What to do when user clicks """
        left, middle, right = mouse_state
        #What got clicked.
        clicked_object = self.determine_clicked(mouse_coords)
        if clicked_object:
            clicked_object.process_click(mouse_coords, mouse_state)
        #What to do given the current state and what got clicked

    def determine_clicked(self, mouse_coords):
        #TODO: see if clicked on a UI element
        
        #see if clicking within the grid
        self.map.process_click(mouse_coords, self.offsets)

        return False

    def process_event(self,event):
        if event.type == self.FRAMEUPDATE:
            self.update()

    def process_keybuffer(self, keybuffer):
        if keybuffer[pygame.K_UP]:
            self.offsets[1] -= 3.0
        if keybuffer[pygame.K_DOWN]:
            self.offsets[1] += 3.0
        if keybuffer[pygame.K_LEFT]:
            self.offsets[0] += 3.0
        if keybuffer[pygame.K_RIGHT]:
            self.offsets[0] -= 3.0
    
    def draw_relative(self):
        """ Draw all map elements """
        self.map.draw(self.offsets)

    def draw_absolute(self):
        """ Draw all UI elements """
        pass

    def move(self, subject, destination):
        pass
