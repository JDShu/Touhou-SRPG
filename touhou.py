import pygame
from OpenGL.GL import *
from math import *

import astar
import ui
import objects
import touhou_characters
import glFreeType
import touhou_events

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
        
        self.draw_floor()
        self.draw_objects()
        
    def draw_highlights(self, highlighted ):
        """highlights tiles in move or attack modes"""
        for tile in highlighted:
            self.tileset["hover"].draw_grid(tile[0],tile[1],self.dimensions, self.offsets)

    def draw_hover(self, tile):
        if tile:
            self.tileset["hover"].draw_grid(tile[0],tile[1],self.dimensions, self.offsets)
        
    def draw_floor(self):
        """Draw the board."""   
        for x in range(self.w):
            for y in range(self.h):
                self.tileset["ground"].draw_grid(x,y,self.dimensions, self.offsets)
                
    def draw_objects(self):
        """Draw Active and Inactive objects"""
        for x in range(self.w):
            x = self.w - x - 1
            for y in range(self.h):
                if self.grid[x][y]:
                    self.grid[x][y].draw_grid(x,y,self.dimensions, self.offsets)
                    

    def temp_tileset(self):
        """Temporary tileset and objects to place on map"""
        tileset = {}
        tileset["ground"] = objects.Graphic(1.0,"grass.png")
        tileset["hover"] = objects.Graphic(0.4,"hover.png")
        tileset["obstacle"] = StaticObject(1.0,"tree.png")
        self.tile_w = 50.0# TODO: replace magic number//sqrt(self.offsets[0]*self.offsets[0] + self.offsets[1]*self.offsets[1])
        return tileset

    def insert(self,instance,position):
        self.grid[position[0]][position[1]] = instance

    def grid_coordinate(self, mouse_coords, offsets):
        """return grid coordinates of mouse click, None if not within grid"""
        mouse_x, mouse_y = mouse_coords
        
        mouse_x -= offsets[0]
        mouse_y -= self.offsets[1] + offsets[1]
        
        
        theta1 = atan(float(self.offsets[0])/float(self.offsets[1]))
        theta2 = atan(float(self.offsets[1])/float(self.offsets[0]))
        x = mouse_x*cos(theta1) + mouse_y*sin(theta1)
        
        y = mouse_x*sin(theta2) - mouse_y*cos(theta2)
        
        max_x = self.tile_w*(self.w)
        max_y = self.tile_w*(self.h)
        
        if 0 < x < max_x and 0 < y < max_y:
            cell_x, cell_y = int(floor((x/max_x)*self.w)), int(floor((y/max_y)*self.h))
            return cell_x, cell_y
        return False

    def process_click(self, mouse_coords, offsets):
        """return object that was clicked on, returns false if nothing"""
        coords = self.grid_coordinate(mouse_coords, offsets)
        if coords:
            return self.grid[coords[0]][coords[1]]
        return False

    def relocate(self, subject, new_position):
        self.grid[new_position[0]][new_position[1]] = subject
        self.grid[subject.position[0]][subject.position[1]] = None
        subject.position = new_position
        
    def occupied(self, position):
        return self.grid[position[0]][position[1]]


class TouhouPlay:
    """The state of a Touhou play session at any given moment"""
    MOVE, ATTACK, BROWSE, WAIT, TURNCHANGE, OPPONENT = range(6)
    TURNCHANGE_INTERVAL = 2000
    def __init__(self, touhou_map):
        """ 
        selectable: Characters that can be clicked on at a given moment
        menu: Menu options available if it is called up
        map: what is currently on the map
        
        """
        self.active = []
        self.main_menu = ui.Menu("Main")
        self.main_menu.add_entry(ui.MenuEntry("End", 0, self.end_turn, 
                                           "menu_option.png",
                                           "menu_option_hover.png", 
                                           "menu_option_clicked.png"))
        self.main_menu.add_entry(ui.MenuEntry("Quit", 1, self.quit,
                                           "menu_option.png",
                                           "menu_option_hover.png", 
                                           "menu_option_clicked.png"))
        self.map = touhou_map
        self.offsets = [0,0,0]
        self.mode = self.BROWSE
        
        self.test_objects()
        self.hover = None
        self.selected = None
        self.menu_on = False
        self.wait_timeleft = 0

        #Custom Events for Touhou Module
        pygame.time.set_timer(touhou_events.FRAMEUPDATE,100)
        pygame.time.set_timer(touhou_events.TENTHSECOND,100)
        
    def quit(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def end_turn(self):
        self.mode = self.TURNCHANGE
        self.wait_timeleft = self.TURNCHANGE_INTERVAL
        self.main_menu.menu_off()
        print "turn ended"

    def test_objects(self):
        position = (4,4)
        reimu = touhou_characters.Reimu(position, self.map, self)
        self.active += [reimu] 
        for x in range(4):
            for y in range(4):
                self.map.insert(self.map.tileset["obstacle"],(x,y))

        self.map.insert(reimu,position)
        self.font = glFreeType.font_data( "free_sans.ttf", 30 )
        #self.active[0].move_cell("N")
        
    def update(self, mouse_coords, mouse_state):
        for a in self.active:
            a.update(mouse_coords, mouse_state)
        self.main_menu.update(mouse_coords, mouse_state)
        if not self.menu_on:
            self.hover = self.map.grid_coordinate(mouse_coords, self.offsets)
        else:
            self.hover = None
        
    def process_click(self, mouse_coords, mouse_state):
        """ What to do when user clicks """
        left, middle, right = mouse_state
        #What got clicked.
        clicked_object = self.determine_clicked(mouse_coords)
                #What to do given the current state and what got clicked
        if self.mode == self.MOVE:
            #print "move"
            if right:
                self.mode = self.BROWSE
            elif left:
                destination = self.map.grid_coordinate(mouse_coords, self.offsets)            
                if destination and self.map.occupied(destination) == None and destination in self.accessible:
                    self.selected.new_path(self.map,destination)
                    self.selected.menu_off()
                    self.mode = self.BROWSE
                    self.selected.ap -= self.selected.move_cost
                    print self.selected.ap

        elif self.mode == self.ATTACK:
            if right:
                self.mode = self.BROWSE
        elif self.mode == self.BROWSE:
            #print "browse"
            if left:
                if not self.menu_on and clicked_object in self.active:
                    self.selected = clicked_object
                    self.selected.menu_on()
                    self.menu_on = True
                    self.selected.menu.set_pos(*mouse_coords)
            elif right:
                if self.menu_on:
                    self.main_menu.menu_off()
                    self.menu_on = False
                    if self.selected:
                        self.selected.menu_off()
                else:
                    
                    self.menu_on = True
                    self.main_menu.set_pos(*mouse_coords)
                    self.main_menu.menu_on()
#self.mode = self.MOVE
        
    def determine_clicked(self, mouse_coords):
        """If UI element is clicked, let element process the click, otherwise, ask map instance what was clicked """
        for a in self.active:
            if a.menu.visible:
                a.menu.process_click()
                return False
        if self.main_menu.visible:
            self.main_menu.process_click()
            return False
        else:
        #see if clicking within the grid
            return self.map.process_click(mouse_coords, self.offsets)


    def process_event(self,event,mouse_coords, mouse_state):
        if event.type == touhou_events.FRAMEUPDATE:
            self.update(mouse_coords, mouse_state)
        if event.type == touhou_events.CLICKEVENT:
            self.menu_on = False
            if event.button == touhou_events.MOVE:
                self.mode = self.MOVE
                self.accessible = self.generate_accessible(event.character)
            elif event.button == touhou_events.ATTACK:
                self.mode = self.ATTACK
                self.attackable = self.generate_attackable(event.character)
            else:
                print "nothin"
        if event.type == touhou_events.TENTHSECOND:
            self.wait_timeleft -= 100
            if self.mode == self.TURNCHANGE and self.wait_timeleft <= 0:
                #should start whoever's turn it is
                print "turn start"
                self.mode = self.BROWSE
                self.menu_on = False
                self.new_turn()

    def new_turn(self):
        """New player turn"""
        for a in self.active:
            a.restore_ap()


    def generate_attackable(self, character):
        temp = [] 
        for a in character.attackable:
            t = (character.position[0] + a[0], character.position[1] + a[1])
            if 0 <= t[0] < self.map.w and 0 <= t[1] < self.map.h and not self.map.grid[t[0]][t[1]]:
                temp += [t]
        return temp

    def generate_accessible(self, character):
        accessible = set()
        accessible.add(character.position)
        for i in xrange(character.SPEED):
            temp = set()
            for c in accessible:
                temp.add((c[0],c[1]-1))
                temp.add((c[0],c[1]+1))
                temp.add((c[0]-1,c[1]))
                temp.add((c[0]+1,c[1]))
            accessible = accessible.union(temp)
            temp = set()
            for t in accessible:
                if not (0 <= t[0] < self.map.w and 0 <= t[1] < self.map.h):
                    temp.add(t)
                elif self.map.grid[t[0]][t[1]]:
                    temp.add(t)
                accessible = accessible.difference(temp)
            
        return accessible

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
        glTranslatef(*self.offsets)
        self.map.draw_floor()
        if self.mode == self.MOVE:
            self.map.draw_highlights(self.accessible)
        if self.mode == self.ATTACK:
            self.map.draw_highlights(self.attackable)
        self.map.draw_objects()
        
        self.map.draw_hover(self.hover)

    def draw_absolute(self):
        """ Draw all UI elements """
        for a in self.active:
            a.menu.draw()
        self.main_menu.draw()
        
    def move_square(self, subject, direction):
        pass
        
class StaticObject(objects.Graphic):
    def __init__(self, a, texture = None, scale_factor = 1.0, w = None, h = None):
        objects.Graphic.__init__(self, a, texture, scale_factor, w, h)

    def process_click(self, mode):
        pass

