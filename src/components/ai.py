class BasicMonster:
    owner = None

    def take_turn(self):
        print(f"The {self.owner.name} wonders when it will get to move.")
