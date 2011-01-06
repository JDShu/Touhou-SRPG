import copy
from heapq import heappush, heappop

class Node():
    def __init__( self, x, y ):
        self.x = x
        self.y = y
        self.open = True
        
    def open_node( self ):
        self.open = True

    def close_node( self ):
        self.open = False
        
    def set_parent( self, parent ):
        self.parent = parent

    def set_g( self, g_cost ):
        self.g = g_cost

    def set_value( self ):
        self.value = self.g + h_function( self )

    def h_function( self, goal):
        temp = [ ( abs( g[0] - self.x) + abs(g[1] - self.y ) ) for g in goal ]
        return min( temp )

    def print_coordinates( self ):
        print ( x, y )

BLOCKED = 1
#2D list data structure for pathfinding
class Grid():
    def __init__( self , touhou_map):
        self.grid = copy.deepcopy(touhou_map.grid)
        self.width, self.height = touhou_map.w, touhou_map.h

    def insert_block( self, x, y ):
        self.grid[x][y] = BLOCKED

    def insert_node( self, x, y, node):
        self.grid[x][y] = node
        
    def print_grid( self ):
        for y in xrange(self.width):
            for x in xrange(self.height):
                if self.grid[y][x] == None:
                    print "0",
                elif self.grid[y][x] == "X":
                    print "X",
                elif self.grid[y][x] == 1:
                    print "W",
                else:
                    print "?",
            print " "
            
    def draw_path( self, path ):
        for sq in path:
            self.grid[sq[0]][sq[1]] = "X"
        self.print_grid()

#generates list of grid coordinates leading from goal to start according to a simple A* algorithm
class Path():
    def __init__( self, input_grid, start, goal ):
        if start == goal:
            self.path = []
            
        self.start = start
        self.goal = goal
        self.grid = copy.deepcopy(input_grid)
        start_node = Node(*start)
        start_node.set_g(0)
        self.grid.insert_node(start[0], start[1], start_node)
        heap = []
        heappush( heap, (0,start) )
        current = heappop(heap)[1]
        reached_goal = False
        if start in goal:
            reached_goal = True
        while not reached_goal:
            c_x, c_y = current
            current_node = self.grid.grid[c_x][c_y]
            current_node.close_node()
            adjacents = self._find_adjacents( current )
            for adj in adjacents:
                a_x, a_y = adj
                node = self.grid.grid[a_x][a_y]
                cost = self._calc_cost( current_node.g, a_x, a_y )
                if node == None:
                    node = Node(*adj)
                    node.set_g( cost )
                    self.grid.insert_node(a_x, a_y, node)
                    value = self._calc_value( node, goal )
                    heappush( heap, (value, adj ) )
                    node.set_parent( current )
                elif node or not node.open:
                    pass
                elif node.open and cost < node.g:
                    node.close_node()
            current = heappop(heap)[1]
            for g in goal:
                if current == g:
                    goal_node = Node(*g)
                    goal_node.set_parent((c_x, c_y),)
                    self.grid.insert_node(g[0], g[1], goal_node)
                    reached_goal = True
        self.path = self._construct_path( current )
                
    def _find_adjacents ( self, current ):
        adjacents = []
        if current[0] > 0:
            adjacents.append( ( current[0] - 1, current[1] ) )
        if current[0] < self.grid.width - 1:
            adjacents.append( ( current[0] + 1, current[1] ) )
        if current[1] > 0:
            adjacents.append( ( current[0], current[1] - 1 ) )
        if current[1] < self.grid.height - 1:
            adjacents.append( ( current[0], current[1] + 1 ) )
        return adjacents

    def _calc_cost ( self, current_g, x, y ):
        return 1 + current_g

    def _calc_value(self, node, goal ):
        return node.g + 1.001*node.h_function( goal )

    def _construct_path( self, goal ):
        if self.start == goal:
            return [goal]
        path = []
        current = goal
        x, y = current
        while current != self.start:
            path.append( current )
            current = self.grid.grid[x][y].parent
            x, y = current
       
        return path
