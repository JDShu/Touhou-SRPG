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
from pygame.locals import *
import pickle

import touhou_level
from touhou_play import TouhouPlay

PLAY = 1
class Touhou:
    def __init__(self, screen_resolution):
        self.name = "Touhou SRPG"
        self.session = None
        self.session_list = {}
        self.running = True

        self.start(screen_resolution)

    def run(self):
        while self.running:
            self.process()
            self.draw()
            self.running = self.session.running

    def load_session(self, s_name):
        self.session = self.session_list[s_name]

    def process(self):
        events = pygame.event.get()
        self.session.process(events)

    def draw(self):
        self.session.gfx_manager.draw()

    def register_session(self,s_name, session):
        self.session_list[s_name] = session

    def start(self, dim):
        pygame.init()
        pygame.display.set_caption(self.name)
        pygame.display.set_mode(dim, OPENGL|DOUBLEBUF)

        #Setup OpenGL
        glOrtho(0.0, dim[0], 0.0, dim[1],-1.0,1.0)
        glClearColor(0.0,0.0,0.0,0.0)

        f = open("./content/level/test.lvl", "r")
        self.level_state = pickle.load(f)
        self.register_session(PLAY,TouhouPlay(self.level_state))
        self.load_session(PLAY)
        self.session.start()
