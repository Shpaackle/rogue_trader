from __future__ import annotations

from components.entity_component import EntityComponent
from constants import CONSTANTS


class Level(EntityComponent):
    def __init__(
        self,
        current_level: int = 1,
        current_xp: int = 0,
        level_up_base: int = CONSTANTS.level_up_base,
        level_up_factor: int = CONSTANTS.level_up_factor,
    ):
        self.current_level: int = current_level
        self.current_xp: int = current_xp
        self.level_up_base: int = level_up_base
        self.level_up_factor: int = level_up_factor

    @property
    def experience_to_next_level(self):
        return self.level_up_base + self.current_level * self.level_up_factor

    def add_xp(self, xp: int) -> bool:
        self.current_xp += xp

        if self.current_xp > self.experience_to_next_level:
            self.current_xp -= self.experience_to_next_level
            self.current_level += 1

            return True
        else:
            return False

    def to_json(self) -> dict:
        json_data = {
            "current_level": self.current_level,
            "current_xp": self.current_xp,
            "level_up_base": self.level_up_base,
            "level_up_factor": self.level_up_factor,
        }
        return json_data

    @classmethod
    def from_json(cls, json_data: dict):
        level = cls(
            current_level=json_data["current_level"],
            current_xp=json_data["current_xp"],
            level_up_base=json_data["level_up_base"],
            level_up_factor=json_data["level_up_factor"],
        )
        return level
