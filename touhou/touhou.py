'''
* This file is part of Touhou SRPG.
* Copyright (c) Hans Lo
*
* Touhou SRPG is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* Touhou SRPG is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with Touhou SRPG.  If not, see <http://www.gnu.org/licenses/>.
'''

import pygame
from OpenGL.GL import *
from math import *
import pygame
from pygame.locals import *

import core.misc.astar
import core.ui
from core.misc.glFreeType import *
from core.module import Module
from core.graphics.graphic import Graphic

import touhou_characters
import touhou_events
import touhou_monsters
import touhou_objects
import touhou_ui
import touhou_level
from touhou_play import TouhouPlay

PLAY = 1
class Touhou(Module):
    def __init__(self):
        #test, TODO: Level class
        Module.__init__(self)
        self.name = "Touhou SRPG"
                
    def start(self, dim):
        pygame.init()
        pygame.display.set_caption(self.name)
        pygame.display.set_mode(dim, OPENGL|DOUBLEBUF)

        #Setup OpenGL
        glOrtho(0.0, dim[0], 0.0, dim[1],-1.0,1.0)
        glClearColor(0.0,0.0,0.0,0.0) 

        self.level_state = touhou_level.TouhouLevel()
        self.register_session(PLAY,TouhouPlay(self.level_state))
        self.load_session(PLAY)
        Module.start_session(self)

class DeprecatedModule:
    """
    Stores classes that define the module:
    map: map of objects in a sigle play session
    play: play session state
    """
    def __init__(self):
        self.map = TouhouMap
        self.play = TouhouPlay

class DeprecatedTouhouMap:
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
        self.gfx = "./content/gfx/sprites/"

        self.grid = []
        for y in xrange(self.h):
            temp = []
            for x in xrange(self.w):
                temp += [None]
            self.grid += [temp]
        self.tileset = self.temp_tileset()
#        self.actors = []
        
    def draw(self,offsets):
        """Draws everything that is on the board."""
        self.draw_floor()
        self.draw_objects()
        
    def draw_highlights(self, highlighted ):
        """highlights tiles in move or attack modes"""
        for tile in highlighted:
            self.tileset["hover"].draw_grid(tile[0],tile[1],self.dimensions, self.offsets)

    def draw_hover(self, tile):
        """highlight a particular tile"""
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
        tileset["ground"] = core.objects.Graphic(1.0, self.gfx + "grass.png")
        tileset["hover"] = core.objects.Graphic(0.4, self.gfx + "hover.png")
        tileset["obstacle"] = StaticObject(1.0, self.gfx + "tree.png")
        self.tile_w = 50.0# TODO: replace magic number//sqrt(self.offsets[0]*self.offsets[0] + self.offsets[1]*self.offsets[1])
        return tileset

    def insert(self,instance,position):
        """change object at a coordinate into something else"""
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
        """move a particular object to a specified coordinate """
        self.grid[new_position[0]][new_position[1]] = subject
        self.grid[subject.position[0]][subject.position[1]] = None
        subject.position = new_position
        
    def occupied(self, position):
        """Return whether or not there is something in the given position"""
        return self.grid[position[0]][position[1]]

    def remove(self, actor):
        """Remove the actor from play."""
        self.grid[actor.position[0]][actor.position[1]] = None
        
        #print self.grid

class DeprecatedTouhouPlay:
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
        self.main_menu = core.ui.Menu("Main")
        self.main_menu.add_entry(core.ui.MenuEntry("End", 0, self.end_turn, 
                                           "menu_option.png",
                                           "menu_option_hover.png", 
                                           "menu_option_clicked.png"))
        self.main_menu.add_entry(core.ui.MenuEntry("Quit", 1, self.quit,
                                           "menu_option.png",
                                           "menu_option_hover.png", 
                                           "menu_option_clicked.png"))
        self.map = touhou_map
        self.offsets = [0,0,0]
        self.mode = self.BROWSE
        
        self.test_objects()
        self.hover = None
        self.selected = None
        self.status_window = touhou_ui.StatusWindow((0,0))
        self.menu_on = False
        self.wait_timeleft = 0

        #Custom Events for Touhou Module
        pygame.time.set_timer(touhou_events.FRAMEUPDATE,100)
        pygame.time.set_timer(touhou_events.TENTHSECOND,100)
        
    def quit(self):
        """Send quit signal to quit game"""
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def end_turn(self):
        """Change states assciated with clicking on the End Turn button"""
        self.mode = self.TURNCHANGE
        self.wait_timeleft = self.TURNCHANGE_INTERVAL
        self.main_menu.menu_off()
        print "turn ended"

    def test_objects(self):
        position = (4,4)
        reimu = touhou_characters.Reimu(position, self.map, self)
        monster = touhou_monsters.Blob((6,5), self.map, self)
        self.active += [reimu]
        self.active += [monster]
        self.map.insert(monster,(6,5))
        for x in range(4):
            for y in range(4):
                self.map.insert(self.map.tileset["obstacle"],(x,y))

        self.map.insert(reimu,position)
        self.font = core.glFreeType.font_data( "./content/font/free_sans.ttf", 30 )
        #self.active[0].move_cell("N")
        
    def update(self, mouse_coords, mouse_state):
        """Update all objects"""
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
                    self.selected.stats.ap -= self.selected.move_cost
                    print self.selected.stats.ap

        elif self.mode == self.ATTACK:
            if left:
                defender = clicked_object
                if defender and defender.type == touhou_objects.MONSTER:
                    self.process_combat(self.selected, defender)
                    #print self.selected, "attacks", defender
                    self.selected.menu_off
                    self.menu_on = False
                    self.mode = self.BROWSE
            elif right:
                self.mode = self.BROWSE
        elif self.mode == self.BROWSE:
            #print "browse"
            if left:
                if not self.menu_on and clicked_object in self.active:
                    self.selected = clicked_object
                    self.status_window.load_stats(clicked_object.stats)
                    self.selected.process_click(mouse_coords, mouse_state)
                    if self.selected.type == touhou_objects.CHARACTER:
                        self.menu_on = True
                    
            elif right:
                if self.menu_on:
                    self.main_menu.menu_off()
                    self.menu_on = False
                    if self.selected and self.selected.type == touhou_objects.CHARACTER:
                        self.selected.menu_off()
                else:
                    
                    self.menu_on = True
                    self.main_menu.set_pos(*mouse_coords)
                    self.main_menu.menu_on()
#self.mode = self.MOVE
        
    def determine_clicked(self, mouse_coords):
        """If UI element is clicked, let element process the click, otherwise, ask map instance what was clicked """
        for a in self.active:
            if a.type == touhou_objects.CHARACTER:
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
        """Read custom events and proccess them"""
        #TODO: Subdivide into smaller functions
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
        """generate list of grid coordinates that are in range of attack by the character"""
        temp = [] 
        for a in character.attackable:
            t = (character.position[0] + a[0], character.position[1] + a[1])
            thing = self.map.grid[t[0]][t[1]]
            if (0 <= t[0] < self.map.w and 0 <= t[1] < self.map.h) and (thing == None or thing.type == touhou_objects.MONSTER):
                temp += [t]
        return temp

    def generate_accessible(self, character):
        """generate list of coordinates that the character is able to move to"""
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
        """Browse around map"""
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
            if a.type == touhou_objects.CHARACTER:
                a.menu.draw()
        self.main_menu.draw()
        self.status_window.draw()

    def move_square(self, subject, direction):
        pass
        

    def process_combat(self, attacker, defender):
        damage = attacker.calculate_damage(defender)
        defender.recieve_damage(damage)
        if defender.is_dead():
            self.remove(defender)

    def remove(self, actor):
        """remove actor from play"""
        self.map.remove(actor)
        self.active.remove(actor)

class DeprecatedStaticObject(Graphic):
    """An object that is just a graphic and takes up space"""
    def __init__(self, a, texture = None, scale_factor = 1.0, w = None, h = None):
        core.objects.Graphic.__init__(self, a, texture, scale_factor, w, h)
        self.type = touhou_objects.OBSTACLE

    def process_click(self, mode):
        pass

