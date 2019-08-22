from __future__ import annotations

from components.entity_component import EntityComponent


class Stairs(EntityComponent):
    def __init__(self, floor: int):
        self.floor: int = floor

    def to_json(self) -> dict:
        json_data = {"floor": self.floor}

        return json_data
