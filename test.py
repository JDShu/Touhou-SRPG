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

# Script to generate a test level.

import pickle

from core.graphics.animated import Animated

from touhou.touhou_level import TouhouLevel, TouhouCreature
from touhou.touhou_names import *

gfx = "./content/gfx/sprites/"
spr = "./content/metadata/"

creatures = []

creatures += [{"name":"reimu", "speed":4, "max_hp":60, "max_ap":100, "creature_type":C_PLAYER }]
creatures += [{"name":"suika", "speed":3, "max_hp":70, "max_ap":100, "creature_type":C_PLAYER }]
creatures += [{"name":"monster", "speed":4, "max_hp":60, "max_ap":100, "creature_type":C_ENEMY }]

positions = {}
positions["reimu"] = (6,3)
positions["suika"] = (6,4)
positions["monster"] = (8,6)

menus = {}
menus["reimu"] = [M_MOVE, M_ATTACK]
menus["suika"] = [M_MOVE, M_ATTACK]

def make_level():
    level = TouhouLevel()
    level.new_map((10,10))

    for c in creatures:
        data = new_data(**c)
        level.map.place_object(None, positions[c["name"]], c["name"])
        level.creatures[c["name"]] = data
        level.menus = menus

    f = open("./content/level/test.lvl", "w")
    pickle.dump(level,f)

def new_data(name = "unnamed", speed=3, max_hp = 100, max_ap = 100, creature_type=None):
    creature = TouhouCreature(name)
    creature.set_max_hp(max_hp)
    creature.set_max_ap(max_ap)
    creature.set_speed(speed)
    creature.set_type(creature_type)
    creature.restore_hp()
    return creature

if __name__ == "__main__":
    make_level()
