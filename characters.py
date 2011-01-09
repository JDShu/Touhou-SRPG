from touhou_objects import PlayerCharacter

class Reimu(PlayerCharacter):
    def __init__(self, touhou_map, touhou):
        PlayerCharacter(self, 15, 15, "reimu", touhou_map, touhou)
