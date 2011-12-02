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

from OpenGL.GL import *

import pygame
from pygame.locals import *
from math import *

from core.graphics.graphic import Graphic, GraphicPositioned, GraphicAbsPositioned
from core.ui import UI

from touhou_menu import Menu
from touhou_graphic import MapGraphic, Highlight
from touhou_names import *


L_CLICK, R_CLICK, L_RELEASE, R_RELEASE = range(4)

GFX_TILE_HOVER = "./content/gfx/sprites/hover.png"
GFX_MENU_BODY = "./content/gfx/gui/menu_body.png"
GFX_MENU_HOVER = "./content/gfx/gui/menu_option.png"

class TouhouUI:

    def __init__(self, level):
        self.ui = UI()
        self.level = level
        self.map = level.map

        self.menus = {}
        self.data = UIData()

        self.left, self.middle, self.right = (0,0,0)

        hover_graphic = Graphic(GFX_TILE_HOVER, 0.5)

        self.hover_tile = MapGraphic(hover_graphic, (0,0), "hover")
        self.highlight = Highlight(hover_graphic)

        self.status_window = StatusWindow(self.level.creatures)
        self.status_window = GraphicAbsPositioned(self.status_window, (0,0))
        self.status_window.make_visible()

        # Status window drawn after sprites.
        self.ui.add(self.status_window)

        # Highlights drawn before sprites.
        self.ui.add_under(self.hover_tile)
        self.ui.add_under(self.highlight)

        #One menu showing at any time
        self.current_menu = None
        
        self.keybuffer = self.new_keybuffer()
        self.mouse_coords = (0,0)
        self.mouse_state = pygame.mouse.get_pressed()

        display = pygame.display.get_surface()
        self.h = display.get_height()

    def new_keybuffer(self):
        keybuffer = []
        for i in range(320):
            keybuffer.append( False )
        return keybuffer

    def key_down(self, e):
        self.keybuffer[e.key] = True

    def key_up(self, e):
        self.keybuffer[e.key] = False

    def update_mouse(self, e):
        x, y = e.pos
        y = self.h - y
        self.mouse_coords = x, y
        self.mouse_state = pygame.mouse.get_pressed()

    def _create_menu(self, name=None):
        menu = Menu(name)
        menu.set_body_graphic(GFX_MENU_BODY)
        menu.set_entry_hover_graphic(GFX_MENU_HOVER)
        menu.set_w(80)
        menu.set_header_height(30)
        menu.set_entry_height(30)
        return menu

    def generate_menus(self):
        self.main_menu = self._create_menu("Main")
        self.main_menu.add_entry("Quit", self.option_quit)
        self.main_menu.add_entry("End Turn", self.end_turn)
        self.main_menu_placed = GraphicAbsPositioned(self.main_menu,(0,0))
        self.ui.add(self.main_menu_placed)

        for m in self.level.menus:
            menu = self._create_menu(m.capitalize())
            for option in self.level.menus[m]:
                if option == M_MOVE:
                    menu.add_entry("Move", self.option_move)
                elif option == M_ATTACK:
                    menu.add_entry("Attack", self.option_attack)

            menu_placed = GraphicAbsPositioned(menu,(0,0))
            self.add_menu(m, menu_placed)

    def end_turn(self):
        pygame.event.post(End_Turn_Event())

    # Attach a name to a menu and add to ui list.
    def add_menu(self, name, menu):
        self.menus[name] = menu
        self.ui.add(menu)

    # Quit program for now.
    def option_quit(self):
        pygame.event.post(pygame.event.Event(QUIT))

    def option_move(self):
        self.data.mode = I_MOVE
        character = self.data.selected
        speed = self.level.creatures[character].speed
        accessible = self.level.generate_accessible(character, speed)
        self.highlight.set_tiles(accessible)
        self.highlight.on()

    def option_attack(self):
        self.data.mode = I_ATTACK
        character = self.data.selected
        attackable = self.level.generate_attackable(character, C_ENEMY)
        self.highlight.set_tiles(attackable)
        self.highlight.on()

    #set selected and current menu to the one specified by given coordinates.
    def set_selected_object(self, pos):
        x,y = pos
        if self.map.grid[x][y]:
            name = self.map.grid[x][y].name
            self.data.selected = name
            try:
                self.current_menu = self.menus[name]
            except KeyError:
                pass

            self.status_window.obj.set_selected(name)
        else:
            self.current_menu = None

    def unselect(self):
        self.data.selected = None
        self.current_menu = None
        self.status_window.obj.unselect()

    def _visible_menu_exists(self):
        if self.current_menu:
            return True
        return False

    def _open_main_menu(self, coords):
        self.current_menu = self.main_menu_placed
        self.current_menu.set_pos(coords)
        self.current_menu.make_visible()

    def _close_current_menu(self):
        self.current_menu.make_invisible()
        self.current_menu = None

    def browse_right_click(self, mouse_coords):
        if self._visible_menu_exists():
            self._close_current_menu()
            self.hover_tile.make_visible()
        else:
            self._open_main_menu(mouse_coords)
            self.hover_tile.make_invisible()

    def browse_left_click(self, mouse_coords):
        if not self._visible_menu_exists():
            self.set_selected_object(self.hover_tile.pos)
            if self.current_menu:
                self.hover_tile.make_invisible()
                self.current_menu.make_visible()
                self.current_menu.set_pos(mouse_coords)
        else:
            if not self.current_menu.visible:
                self.current_menu.make_visible()
                self.current_menu.set_pos(mouse_coords)
            else:
                self.current_menu.obj.log_pending()

    def browse_left_release(self, mouse_coords):
        if self.current_menu and self.current_menu.obj.pending != None:
            self.current_menu.obj.execute_entry()
            self.current_menu.obj.clear_pending()
            self.current_menu.make_invisible()
            self.hover_tile.make_visible()

    def move_right_click(self, mouse_coords):
        self.data.mode = I_BROWSE
        self.highlight.off()
        self.current_menu = None

    def attack_right_click(self, mouse_coords):
        self.data.mode = I_BROWSE
        self.highlight.off()
        self.current_menu = None

    def move_left_click(self, mouse_coords):
        pass

    def move_left_release(self, mouse_coords):
        x,y = self.hover_tile.pos
        if (x,y) in self.highlight.set:
            pygame.event.post(Move_Event(self.data.selected, (x,y)))
            self.data.locked = True
            self.current_menu = None
            self.highlight.off()

    def attack_left_release(self, mouse_coords):
        x,y = self.hover_tile.pos
        if (x,y) in self.highlight.set:
            pygame.event.post(Attack_Event(self.data.selected, (x,y)))
            self.current_menu = None
            self.highlight.off()
            self.data.mode = I_BROWSE

    def set_browse(self):
        self.data.dest = None
        self.data.mode = I_BROWSE
        self.data.locked = False

    def user_action(self, mouse_state):
        new_left, new_middle, new_right = mouse_state
        if new_left and not self.left:
            return L_CLICK
        elif not new_left and self.left:
            return L_RELEASE
        elif new_right and not self.right:
            return R_CLICK
        elif not new_right and self.right:
            return R_RELEASE

    def browse_actions(self, action, mouse_coords):
        if action == L_CLICK:
            self.browse_left_click(mouse_coords)
        elif action == L_RELEASE:
            self.browse_left_release(mouse_coords)
        elif action == R_CLICK:
            self.browse_right_click(mouse_coords)

    def move_actions(self, action, mouse_coords):
        if action == L_RELEASE:
            self.move_left_release(mouse_coords)
        elif action == R_CLICK:
            self.move_right_click(mouse_coords)

    def attack_actions(self, action, mouse_coords):
        if action == L_RELEASE:
            self.attack_left_release(mouse_coords)
        elif action == R_CLICK:
            self.attack_right_click(mouse_coords)

    def update(self, map_offset):
        if not self.data.locked:
            action = self.user_action(self.mouse_state)
            if self.data.mode == I_BROWSE:
                self.browse_actions(action, self.mouse_coords)
            elif self.data.mode == I_MOVE:
                self.move_actions(action, self.mouse_coords)
            elif self.data.mode == I_ATTACK:
                self.attack_actions(action, self.mouse_coords)

        hover = self.map.get_square(self.mouse_coords, map_offset)
        if hover:
            self.hover_tile.set_pos(hover)

        # now we can update the mouse state
        self.left, self.middle, self.right = self.mouse_state
        x,y = self.mouse_coords

        if self.current_menu:
            x2, y2 = self.current_menu.get_pos()
            rel_coords = (x-x2,y-y2)
            self.current_menu.obj.update(rel_coords)

def UI_Event(self, subtype=None):
    e = pygame.event.Event(UI_EVENT)
    e.subtype = subtype
    return e

# Notify creature's intention to move to a certain destination.
def Move_Event(creature=None, destination=None):
    e = pygame.event.Event(UI_EVENT, subtype=MOVETO, name=creature, dest=destination)
    return e

def Attack_Event(a_attacker, a_target):
    e = pygame.event.Event(UI_EVENT, subtype=ATTACK, attacker=a_attacker, target=a_target)
    return e

def End_Turn_Event():
    e = pygame.event.Event(UI_EVENT, subtype=ENDTURN)
    return e

class UIData:
    def __init__(self):
        self.mode = I_BROWSE
        self.hover = None
        self.locked = False

        self.selected = None
        self.dest = None

class StatusWindow:
    gfx = "./content/gfx/gui/"
    """Collection of elements that describe character/monster"""
    def __init__(self, creatures_table):
        #test graphic
        self.health_bar_gfx = HorizontalBar(self.gfx+"health_bar.png")

        # Get data from here.
        self.table = creatures_table

        self.portrait_list = {}
        self.setup_portraits()

        self.portrait = StatusElement(None, (0.0,0.0))
        self.health_bar = StatusElement(None, (80.0,80.0))
        self.stats = None
        self.visible = True

        self.elements = []

        self.add_element(self.health_bar)
        self.add_element(self.portrait)

    def add_element(self, element):
        self.elements += [element]

    def setup_portraits(self):
        for c in self.table:
            self.portrait_list[c] = Graphic("./content/gfx/sprites/"+c+"_portrait.png")

    def set_selected(self, name):
        self.portrait.element = self.portrait_list[name]
        self.health_bar.element = self.health_bar_gfx
        hp = self.table[name].hp
        max_hp = self.table[name].max_hp
        self.health_bar_gfx.set_value(hp, max_hp)

    def unselect(self):
        self.portrait.element = None
        self.health_bar.element = None

    def window_off(self):
        self.visible = False

    def update(self):
        pass

    def draw(self):
        for e in self.elements:
            if e.element:
                x,y = e.position
                glPushMatrix()
                glTranslate(x,y,0)
                e.element.draw()
                glPopMatrix()

class StatusElement:
    def __init__(self, element, position):
        self.element = element
        self.position = position

class HorizontalBar:
    """Bar that has a length that depends on the value, eg. a health bar"""
    def __init__(self, image, length=100.0):
        self.image = Graphic(image)
        self.base_length = float(length)
        self.image.w = self.base_length
        self.image.setup_draw()
        self.max_value = None

    def set_value(self, value, max_value):
        value = float(value)
        max_value = float(max_value)
        self.image.w = value/max_value * self.base_length
        self.image.setup_draw()

    def set_max(self, max_value):
        self.max_value = float(max_value)

    def draw(self):
        self.image.draw()
