import objects

class StatusWindow:
    """Collection of elements that describe character/monster"""
    def __init__(self, coords):
        self.portrait = None
        self.stats = None
        self.health_bar = HorizontalBar("health_bar.png")
        self.visible = False
        self.coords = coords

    def load_stats(self, stats):
        self.stats = stats
        self.health_bar.load_stats(self.stats.hp, self.stats.MAX_HP)
        self.visible = True

    def window_off(self):
        self.visible = False

    def update(self):
        self.health_bar.set_value(self.stats.hp)

    def draw(self):
        x,y = self.coords
        if self.visible:
            self.stats.portrait.draw(x,y)
            x += 150
            y += 70
            self.health_bar.draw(x,y)

class HorizontalBar:
    """Bar that has a length that depends on the value, eg. a health bar"""
    def __init__(self, image):
        self.image = objects.DynamicGraphic(1.0, image)
        self.image.w = 300.0
        self.image.setup_draw()
        self.max_value = None
        self.current_calue = None
        

    def load_stats(self, current_value, max_value):
        self.current_value = current_value
        self.max_value = max_value

    def set_value(self, value):
        self.current_value = value

    def draw(self, x, y):
        self.image.draw(x, y)
    
