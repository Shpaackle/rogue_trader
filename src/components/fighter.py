from __future__ import annotations

from typing import List, TYPE_CHECKING

from colors import Colors
from components.entity_component import EntityComponent
from game_messages import Message

if TYPE_CHECKING:
    from entity import Entity


class Fighter(EntityComponent):
    def __init__(
        self, hp: int, defense: int, power: int, max_hp: int = None, xp: int = 0
    ):
        super(Fighter, self).__init__()
        self.hp: int = hp
        self.base_defense: int = defense
        self.base_power: int = power
        self.xp: int = xp

        if max_hp is None:
            self.base_max_hp: int = hp
        else:
            self.base_max_hp: int = max_hp

    @property
    def max_hp(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.max_hp_bonus
        else:
            bonus = 0
        return self.base_max_hp + bonus

    @property
    def power(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.power_bonus
        else:
            bonus = 0
        return self.base_power + bonus

    @property
    def defense(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.defense_bonus
        else:
            bonus = 0
        return self.base_defense + bonus

    def take_damage(self, amount: int):
        results: List[dict] = []

        self.hp -= amount

        if self.hp <= 0:
            results.append({"dead": self.owner, "xp": self.xp})

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
            "base_max_hp": self.base_max_hp,
            "hp": self.hp,
            "base_defense": self.base_defense,
            "base_power": self.base_power,
            "xp": self.xp,
        }

        return json_data

    @classmethod
    def from_json(cls, json_data) -> Fighter:
        fighter: Fighter = cls(
            hp=json_data.get("hp"),
            defense=json_data.get("base_defense"),
            power=json_data.get("base_power"),
            max_hp=json_data.get("base_max_hp"),
            xp=json_data.get("xp", 0),
        )

        return fighter
