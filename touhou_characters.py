from touhou_objects import *
from ui import *
import glFreeType
import pygame
import touhou_events

class Reimu(PlayerCharacter):
    def __init__(self, position, touhou_map, touhou):
        PlayerCharacter.__init__(self, 15, 15, "reimu", position, touhou_map, touhou)
        self.menu = ReimuMenu()
        
    def menu_on(self):
        """Turn the menu on """
        self.menu.visible = True

    def menu_off(self):
        """Turn the menu off"""
        self.menu.visible = False
        
class ReimuMenu(Menu):
    def __init__(self, font = None):
        Menu.__init__(self, "Reimu")
        self.add_entry(MenuEntry("Move", self.move_function, "menu_option.png","menu_option_hover.png", "menu_option_clicked.png"))

    def draw(self):
        if self.visible:
            Menu.draw(self)

    def move_function(self):
        pygame.event.post(pygame.event.Event(touhou_events.MOVEMODE))
