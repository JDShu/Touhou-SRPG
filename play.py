import pygame
from math import *

import level
import events
import ui
import glFreeType
from objects import *
import actions

SCALE = 0.5

BROWSE, MOVE = xrange(2)

class Play_State:
    def __init__( self, level ):
        self.mode = BROWSE
        self.level = level
    def set_state(self, state):
        print "state: ", state
        self.mode = state
        
#map file, scenario file, characters
class Play:
    def __init__( self, w,h ):

        def f(x):
            print x
        def g(x):
            print x + 1
        
        self.level = None
        self.new_keybuffer()
        self.reimu_test = Character("reimu2.png",9,2,"reimu_portrait.png",None,SCALE)
        self.reimu_menu = ui.Menu("Reimu")
        self.reimu_menu.add_entry(ui.Menu_Entry("Move", actions.move, "menu_option.png","menu_option_hover.png", "menu_option_clicked.png"))
        self.test_menu = ui.Menu("Title")
        self.test_menu.add_entry(ui.Menu_Entry("1", f, "menu_option.png","menu_option_hover.png", "menu_option_clicked.png"))
        self.test_menu.add_entry(ui.Menu_Entry("2", g, "menu_option.png","menu_option_hover.png", "menu_option_clicked.png"))
        self.w, self.h = w, h
        self.font = glFreeType.font_data( "free_sans.ttf", 30 )
        self.selected_character = None
        
        
    def new_keybuffer( self ):
        self.keybuffer = []
        for i in range(320):
            self.keybuffer.append( False )
        
    def process( self ):
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_y = self.h - mouse_y
        l_click, m_click, r_click = pygame.mouse.get_pressed()

        self.hover_square = self.get_mouse_square(mouse_x,mouse_y)

        if self.hover_square == self.reimu_test.position:
            self.hover_character = self.reimu_test
        else:
            self.hover_character = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                self.keybuffer[ event.key ] = True
            elif event.type == pygame.KEYUP:
                self.keybuffer[ event.key ] = False
            elif event.type == pygame.USEREVENT + 1:
                self.reimu_test.anim_update()
            elif event.type == pygame.USEREVENT + 2:
                self.reimu_test.pos_update()
        
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pass
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.play_state.mode == BROWSE:
                    if r_click:
                        self.test_menu.set_pos(mouse_x, mouse_y)
                        self.test_menu.toggle()
                        self.reimu_menu.visible = False
                        self.selected_character = None
                    elif l_click:
                        self.test_menu.process_click(1)
                        self.reimu_menu.process_click(self.play_state)
                        if self.hover_square == self.reimu_test.position:
                            self.selected_character = self.reimu_test
                            self.reimu_menu.set_pos(mouse_x, mouse_y)
                            self.reimu_menu.visible = True
                        

                elif self.play_state.mode == MOVE:
                    if r_click:
                        if self.selected_character.moving == self.selected_character.MOVING:
                            self.selected_character.revert()
                        elif self.selected_character.moving == self.selected_character.MOVED:
                            self.selected_character.confirm()
                            print "1"
                            self.play_state.set_state(BROWSE)
                        else:
                            print "2"
                            self.play_state.set_state(BROWSE)
                            
                    if l_click and not self.selected_character.moving:
                        if self.hover_square:
                            self.selected_character.move_to(*self.hover_square)
                    
                    

        #if self.play_state.mode == MOVE:
        #    if self.selected_character.moving == self.selected_character.MOVED:
        #        self.play_state.set_state(BROWSE)
        #        print "3"
#scroll around map
        if self.keybuffer[pygame.K_UP]:
            self.up_offset -= 3.0
        if self.keybuffer[pygame.K_DOWN]:
            self.up_offset += 3.0
        if self.keybuffer[pygame.K_LEFT]:
            self.left_offset += 3.0
        if self.keybuffer[pygame.K_RIGHT]:
            self.left_offset -= 3.0

        self.test_menu.update((mouse_x,mouse_y),l_click)
        self.reimu_menu.update((mouse_x,mouse_y),l_click)
        return True
    
    def draw( self ):
        
#draw map
        glPushMatrix()
        glTranslatef(self.left_offset,self.up_offset,0.0)
        self.draw_map()
#        self.reimu_test.actor.setup_draw()
        self.reimu_test.actor.Draw()
        glPopMatrix()
#        self.test_menu.Draw()
        self.reimu_menu.Draw()
        if self.hover_character:
            self.hover_character.portrait.Draw()
        elif self.selected_character:
            self.selected_character.portrait.Draw()
            
        
    def load_map( self, level_map ):
        pass

    def draw_map( self ):
        self.level.ground_tile.setup_draw()
        for x in xrange(self.level.w):
            for y in xrange(self.level.h):
                self.level.ground_tile.set_pos(x,y)
                self.level.ground_tile.Draw()
        if self.hover_square:
            self.level.hover_tile.set_pos(*self.hover_square)
            self.level.hover_tile.Draw()
            
            
    def load_level( self, level ):
        self.level = level
        self.left_offset, self.up_offset = 0, 0
        self.reimu_test.set_pos(0,0)
        t_offsets = self.level.tile_offsets
        self.tile_w = sqrt(pow(t_offsets[0],2) + pow(t_offsets[1],2))
        self.tile_h = self.tile_w
        self.play_state = Play_State(self.level)
        
    def get_mouse_square(self, mouse_x, mouse_y ):
        
        t_offsets = self.level.tile_offsets
        t_dimensions = self.level.tile_dimensions
        mouse_x -= self.left_offset + t_offsets[0]
        mouse_y -= self.up_offset
        theta1 = atan(t_offsets[0]/t_offsets[1])
        theta2 = atan(t_offsets[1]/t_offsets[0])
        x = mouse_x*cos(theta1) + mouse_y*sin(theta1)
        y = -mouse_x*sin(theta2) + mouse_y*cos(theta2)
        max_x = self.tile_w*(self.level.w-1)
        max_y = self.tile_h*(self.level.h-1)
        if 0 < x < max_x and 0 < y < max_y:
            return floor((x/max_x)*self.level.w), floor((y/max_y)*self.level.h)
        else:
            return False
