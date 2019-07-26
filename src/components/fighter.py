class Fighter:
    def __init__(self, hp: int, defense: int, power: int):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power
        self.owner = None

    def take_damage(self, amount: int):
        results = []

        self.hp -= amount

        if self.hp <= 0:
            results.append({"dead": self.owner})

        return results

    def attack(self, target: "Entity"):
        results = []

        damage = self.power - target.fighter.defense

        if damage > 0:
            target.fighter.take_damage(amount=damage)
            results.append({"message": f"{self.owner.name.capitalize()} attacks {target.name} for {str(damage)} hit points."})
            results.extend(target.fighter.take_damage(damage))
        else:
            results.append({"message": f"{self.owner.name.capitalize()} attacks {target.name} but does no damage."})

        return results
