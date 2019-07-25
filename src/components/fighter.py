class Fighter:
    def __init__(self, hp: int, defense: int, power: int):
        self.max_hp = hp
        self.defense = defense
        self.power = power
        self.owner = None
