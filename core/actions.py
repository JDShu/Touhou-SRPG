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

import level

BROWSE, MOVE = xrange(2)

def print_w(play_state):
    print play_state.level.w

def move(play_state, character):
    play_state.set_state(MOVE)
    character.find_accessible(play_state.level)

def revert(play_state, character):
    play_state.level.relocate(character.position,character.before_position,  "X")
    character.revert()
    
def confirm(play_state, character):
    play_state.level.relocate(character.before_position, character.position,  "X")
    character.confirm()
    play_state.set_state(BROWSE)
    
