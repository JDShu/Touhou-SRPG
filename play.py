import pygame
from math import *

import level
import events
import ui
import glFreeType
from objects import *
import actions
import stats
import astar

SCALE = 0.5

BROWSE, MOVE = xrange(2)

class Play_State:
    def __init__( self, level ):
        self.mode = BROWSE
        self.level = level
        #temporary touhou specific menus
        self.menus = {}
        self.menus["reimu"] = ui.Menu("Reimu")
        self.menus["reimu"].add_entry(ui.Menu_Entry("Move", actions.move, "menu_option.png","menu_option_hover.png", "menu_option_clicked.png"))
        self.menus["move_confirm"] = ui.Menu("OK?")
        self.menus["move_confirm"].add_entry(ui.Menu_Entry("Yes", actions.confirm, "menu_option.png","menu_option_hover.png", "menu_option_clicked.png"))
        self.menus["move_confirm"].add_entry(ui.Menu_Entry("No", actions.revert, "menu_option.png","menu_option_hover.png", "menu_option_clicked.png"))
        
        
    def set_state(self, state):
        #print "state: ", state
        self.mode = state
        
#map file, scenario file, characters
class Play:
    def __init__( self, w,h ):

        def f(x):
            print x
        def g(x):
            print x + 1
        
        self.new_keybuffer()
        self.reimu_stats = stats.Stats(100, 4)
        self.reimu_test = Character("reimu.png",9,2,"reimu_portrait.png",self.reimu_stats,SCALE)
        self.w, self.h = w, h
        self.font = glFreeType.font_data( "free_sans.ttf", 30 )
        self.selected_character = None
        self.tree_test = Graphic(0.0,0.0,1.0,"tree.png",SCALE)
        
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
                self.reimu_test.move()
            elif event.type == pygame.USEREVENT + 3:
                self.play_state.menus["move_confirm"].set_pos(mouse_x, mouse_y)
                self.play_state.menus["move_confirm"].visible = True
                self.play_state.level.relocate(self.selected_character.previous_node,self.selected_character.position,  "X")
            elif event.type == pygame.USEREVENT + 4:
                self.play_state.level.relocate(self.selected_character.previous_node,self.selected_character.position,  "X")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pass
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.play_state.mode == BROWSE:
                    if r_click:
                        #self.test_menu.set_pos(mouse_x, mouse_y)
                        #self.test_menu.toggle()
                        self.play_state.menus["reimu"].visible = False
                        self.selected_character = None
                    elif l_click:
                        #self.test_menu.process_click(1)
                        for m in self.play_state.menus:
                            self.play_state.menus[m].process_click(self.play_state, self.selected_character)
                        if self.hover_square == self.reimu_test.position:
                            self.selected_character = self.reimu_test
                            self.play_state.menus["reimu"].set_pos(mouse_x, mouse_y)
                            self.play_state.menus["reimu"].visible = True
                        

                elif self.play_state.mode == MOVE:
                    #calculate and display accessible tiles
                    
                    if l_click and not self.selected_character.moving:
                        if self.hover_square:
                            self.selected_character.move_to(self.play_state.level, self.hover_square)

                    if self.selected_character.moving == self.selected_character.MOVED:
                        for m in self.play_state.menus:
                            self.play_state.menus[m].process_click(self.play_state, self.selected_character)
                        if r_click:
                            actions.revert(self.play_state, self.selected_character)
                            self.play_state.menus["move_confirm"].visible = False

#scroll around map
        if self.keybuffer[pygame.K_UP]:
            self.up_offset -= 3.0
        if self.keybuffer[pygame.K_DOWN]:
            self.up_offset += 3.0
        if self.keybuffer[pygame.K_LEFT]:
            self.left_offset += 3.0
        if self.keybuffer[pygame.K_RIGHT]:
            self.left_offset -= 3.0
        for m in self.play_state.menus:
            self.play_state.menus[m].update((mouse_x,mouse_y),l_click)
        return True
    
    def draw( self ):
        
#draw map
        glPushMatrix()
        glTranslatef(self.left_offset,self.up_offset,0.0)
        self.draw_map()
#        self.reimu_test.actor.setup_draw()
        
                            
        glPopMatrix()
        for m in self.play_state.menus:
            self.play_state.menus[m].Draw()
        if self.hover_character:
            self.hover_character.portrait.Draw()
        elif self.selected_character:
            self.selected_character.portrait.Draw()

            
    def load_map( self, level_map ):
        pass

    def draw_map( self ):
        objects = []
        self.play_state.level.ground_tile.setup_draw()
        for x in xrange(self.play_state.level.w):
            for y in xrange(self.play_state.level.h):
                self.play_state.level.ground_tile.set_pos(x,y)
                self.play_state.level.ground_tile.Draw()
                if self.play_state.level.map[x][y]:
                    objects += [(self.play_state.level.map[x][y],(x,y))]
        if self.play_state.mode == MOVE:
            for t in self.selected_character.accessible:
                #if 0 <= t[0] < self.play_state.level.w and 0 <= t[1] <self.play_state.level.h:
                self.play_state.level.hover_tile.set_pos(*t)
                self.play_state.level.hover_tile.Draw()
        if self.hover_square:
            self.play_state.level.hover_tile.set_pos(*self.hover_square)
            self.play_state.level.hover_tile.Draw()
        #draw obstacles
        for o in reversed(objects):
            if o[0] == "T":
                self.tree_test.set_map_pos(*o[1])
                self.tree_test.Draw()
            if o[0] == "X":
                self.reimu_test.actor.Draw()

    def load_level( self, level ):
        self.play_state = Play_State(level)
        self.left_offset, self.up_offset = 0, 0
        self.reimu_test.set_pos(5,5)
        self.play_state.level.insert((5,5),"X")
        self.play_state.level.insert((7,7),"T")
        self.play_state.level.insert((7,6),"T")
        self.play_state.level.insert((7,5),"T")
        self.play_state.level.insert((4,7),"T")
        t_offsets = level.tile_offsets
        self.tile_w = sqrt(pow(t_offsets[0],2) + pow(t_offsets[1],2))
        self.tile_h = self.tile_w
        
        
    def get_mouse_square(self, mouse_x, mouse_y ):
        
        t_offsets = self.play_state.level.tile_offsets
        t_dimensions = self.play_state.level.tile_dimensions
        mouse_x -= self.left_offset + t_offsets[0]
        mouse_y -= self.up_offset
        theta1 = atan(t_offsets[0]/t_offsets[1])
        theta2 = atan(t_offsets[1]/t_offsets[0])
        x = mouse_x*cos(theta1) + mouse_y*sin(theta1)
        y = -mouse_x*sin(theta2) + mouse_y*cos(theta2)
        max_x = self.tile_w*(self.play_state.level.w-1)
        max_y = self.tile_h*(self.play_state.level.h-1)
        if 0 < x < max_x and 0 < y < max_y:
            return floor((x/max_x)*self.play_state.level.w), floor((y/max_y)*self.play_state.level.h)
        else:
            return False
