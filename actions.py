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
    
