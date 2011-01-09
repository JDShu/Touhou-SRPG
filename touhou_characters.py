from touhou_objects import *
from ui import *
import glFreeType

class Reimu(PlayerCharacter):
    def __init__(self, position, touhou_map, touhou):
        PlayerCharacter.__init__(self, 15, 15, "reimu", position, touhou_map, touhou)
        self.menu = ReimuMenu()
        

    def menu_on(self):
        """Turn the menu on """
        self.menu.visible = True
        print "menu on"

    def menu_off(self):
        """Turn the menu off"""
        self.menu.visible = False
        print "menu off"
        
class ReimuMenu(Menu):
    def __init__(self, font = None):
        Menu.__init__(self, "Reimu")
        
    def draw(self):
        if self.visible:
            Menu.draw(self)
        
