from __future__ import annotations

from typing import List, TYPE_CHECKING

from colors import Colors
from components.entity_component import EntityComponent
from game_messages import Message

if TYPE_CHECKING:
    from entity import Entity


class Fighter(EntityComponent):
    def __init__(self, hp: int, defense: int, power: int, max_hp: int = None):
        super(Fighter, self).__init__()
        self.hp: int = hp
        self.defense: int = defense
        self.power: int = power

        if max_hp is None:
            self.max_hp: int = hp
        else:
            self.max_hp: int = max_hp

    def take_damage(self, amount: int):
        results: List[dict] = []

        self.hp -= amount

        if self.hp <= 0:
            results.append({"dead": self.owner})

        return results

    def attack(self, target: Entity):
        results: List[dict] = []

        damage: int = self.power - target.fighter.defense

        if damage > 0:
            # target.fighter.take_damage(amount=damage)
            results.append(
                {
                    "message": Message(
                        f"{self.owner.name.capitalize()} attacks {target.name} for {str(damage)} hit points.",
                        Colors.WHITE,
                    )
                }
            )
            results.extend(target.fighter.take_damage(damage))
        else:
            results.append(
                {
                    "message": Message(
                        f"{self.owner.name.capitalize()} attacks {target.name} but does no damage.",
                        Colors.WHITE,
                    )
                }
            )

        return results

    def heal(self, amount: int):
        self.hp += amount

        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def to_json(self):
        json_data = {
            "max_hp": self.max_hp,
            "hp": self.hp,
            "defense": self.defense,
            "power": self.power
        }

        return json_data

    @classmethod
    def from_json(cls, json_data) -> Fighter:
        fighter: Fighter = cls(
            hp=json_data.get("hp"),
            defense=json_data.get("defense"),
            power=json_data.get("power"),
            max_hp=json_data.get("max_hp")
        )

        return fighter
