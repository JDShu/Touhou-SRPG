import touhou_objects

class Monster(touhou_objects.Actor):
    def __init__(self, x,y,sprite_name, position, touhou_map, touhou, scale_factor = 1.0):
        touhou_objects.Actor.__init__(self, x,y,sprite_name, position, touhou_map, touhou, scale_factor)
        self.menu = None
        self.type = touhou_objects.MONSTER
        

    def set_menu(self, menu):
        self.menu = menu
        
    def move_inc(self):
        touhou_objects.Actor.move_inc(self)
        
    def update(self, mouse_coords, mouse_state):
        touhou_objects.Actor.update(self)
        
class Blob(Monster):
    MAX_AP = 100
    MAX_HP = 100

    def __init__(self, position, touhou_map, touhou):
        Monster.__init__(self, 15, 15, "monster", position, touhou_map, touhou, 0.8)
        self.hp = self.MAX_HP
        self.ap = self.MAX_AP

    def restore_ap(self):
        self.ap = self.MAX_AP

    def calculate_damage(self, defender):
        return 30

    def recieve_damage(self, damage):
        self.hp -= damage

    def is_dead(self):
        return self.hp <= 0
