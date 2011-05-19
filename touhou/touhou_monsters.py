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
from touhou_objects import *

class Monster(Actor):
    def __init__(self, x,y,sprite_name, position, touhou_map, touhou, scale_factor = 1.0):
        Actor.__init__(self, x,y,sprite_name, position, touhou_map, touhou, scale_factor)
        self.menu = None
        self.type = MONSTER
        

    def set_menu(self, menu):
        self.menu = menu
        
    def move_inc(self):
        Actor.move_inc(self)
        
    def update(self, mouse_coords, mouse_state):
        Actor.update(self)
        
class Blob(Monster):
    MAX_AP = 100
    MAX_HP = 100

    def __init__(self, position, touhou_map, touhou):
        Monster.__init__(self, 15, 15, "monster", position, touhou_map, touhou, 0.8)
        self.stats = Stats(self.MAX_HP, self.MAX_AP, "monster.png")

    def restore_ap(self):
        self.stats.ap = self.MAX_AP

    def calculate_damage(self, defender):
        return 30

    def recieve_damage(self, damage):
        self.stats.hp -= damage

    def is_dead(self):
        return self.stats.hp <= 0
