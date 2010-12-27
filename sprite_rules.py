class Sprite:
    def __init__(self, filename):
        self.filename = filename
        self.actions = {}
        
    def set_frame(self, name, frame, dimensions):
        if name not in self.actions:
            self.actions[name] = []
    
        length = len(self.actions[name])
        while frame >= length:
            length += 1
            self.actions[name] += [None]
        self.actions[name][frame] = dimensions
