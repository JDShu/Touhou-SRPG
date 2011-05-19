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
# Play_State: Class that tracks the game state at any given instance. Offers functions to modify the state.

# actors: list of all actors
# selectable: list of characters that can be controlled at any time
# menu: list of options currently available in a menu
# map: map terrain and where objects on the map are


class Rules:
    def __init__(self):
        pass

    def combat(self, attacker, defender):
        pass

    def options(self, character):
        pass

    def main_menu(self):
        pass
