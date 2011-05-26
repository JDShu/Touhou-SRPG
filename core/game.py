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

# Organizes everything together.
class Game:
    def __init__(self):
        self.running = False

    # Load the central module file, eg. touhou
    def load_module(self, module):
        self.module = module()

    def start(self):
        self.running = True
        self.module.start((640,480))

    def stop(self):
        self.running = False
        
    def process(self):
        while(self.running):
            self.module.process()
            self.module.draw()
            self.running = self.module.session_running()

    def run(self):
        self.start()
        self.process()
