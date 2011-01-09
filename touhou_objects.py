from OpenGL.GL import *
import objects
import astar

class Actor(objects.Animated):
    MOVING, IDLE = range(2)
    TICKS = 10
    def __init__(self, x,y,sprite_name, position, touhou_map, touhou, scale_factor = 1.0):
        objects.Animated.__init__(self, x,y,sprite_name, scale_factor = 1.0)
        self.selected = False
        self.set_cell_offsets(0,0)
        self.position = position
        self.state = self.IDLE
        self.tile_offsets = touhou_map.offsets
        self.map = touhou_map
        self.path = []
        self.direction = None
        self.ticks = 0
        self.play = touhou
        

    def process_click(self, mode):
        pass

    def draw_grid(self, x, y, dimensions, offsets):
        glPushMatrix()
        glTranslatef(self.cell_offset_x, self.cell_offset_y, 0.0)
        objects.Animated.draw_grid(self, x, y, dimensions, offsets)
        glPopMatrix()
        
    def set_cell_offsets(self, x, y):
        self.cell_offset_x, self.cell_offset_y = x, y

    def mod_cell_offsets(self, x, y):
        self.cell_offset_x += x
        self.cell_offset_y += y

    def move_cell(self, direction):
        self.state = self.MOVING
        self.direction = direction
        self.ticks = 0

    def move_inc(self):
        """Move subject incrementally in a direction until it reaches one cell away"""
        if self.direction == "N":
            d = (1,1) 
            p = (1,0)
        elif self.direction == "S":
            d = (-1,-1)
            p = (-1,0)
        elif self.direction == "E":
            d = (1,-1)
            p = (0,1)
        elif self.direction == "W":
            d = (-1,1)
            p = (0,-1)
        else:
            d = (0,0)
            p = (0,0)

        self.mod_cell_offsets(d[0]*self.tile_offsets[0]/10.0, d[1]*self.tile_offsets[1]/10.0)
        self.ticks += 1
        #print self.ticks
        if self.ticks >= self.TICKS:
            #self.state = self.IDLE
            self.map.relocate(self, (self.position[0] + p[0],self.position[1] + p[1]))
            self.set_cell_offsets(0.0,0.0)
            self.path = self.path[:-1]
            self.move_to_destination()
            self.ticks = 0
                        

    def move_to_destination(self):
        
        if self.path:
            next_cell = self.path[-1]
            direction = next_cell[0] - self.position[0], next_cell[1] - self.position[1]
            
            if direction == (0,1):
                self.direction = "E"
                self.current_action = "idle-e"
            elif direction == (0,-1):
                self.direction = "W"
                self.current_action = "idle-w"
            elif direction == (1,0):
                self.direction = "N"
                self.current_action = "idle-n"
            elif direction == (-1,0):
                self.direction = "S"
                self.current_action = "idle-s"
            
        else:
            self.state = self.IDLE
            self.play.mode = self.play.BROWSE
            
        
    def update(self):
        objects.Animated.update(self)
        if self.state == self.MOVING:
            self.move_inc()
        
    def new_path(self, touhou_map, destination):
        self.state = self.MOVING
        grid = astar.Grid(touhou_map)
        path = astar.Path(grid, self.position, [destination])
        self.path = path.path
        print self.path
        self.move_to_destination()

class StaticObject(objects.Graphic):
    def __init__(self, a, texture = None, scale_factor = 1.0, w = None, h = None):
        objects.Graphic.__init__(self, a, texture, scale_factor, w, h)

    def process_click(self, mode):
        pass

class PlayerCharacter(Actor):
    def __init__(self, x,y,sprite_name, position, touhou_map, touhou, scale_factor = 1.0):
        Actor.__init__(self, x,y,sprite_name, position, touhou_map, touhou, scale_factor = 1.0)
        self.menu = None

    def set_menu(self, menu):
        self.menu = menu
        print "set menu"

    def move_inc(self):
        Actor.move_inc(self)
        
