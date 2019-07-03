from typing import List

from entity import Entity
from map_objects import GameMap


def render_all(entities: List[Entity], game_map: GameMap, colors: dict):
    # Draw the map
    game_map.render(colors=colors)

    # Draw all entities in the list
    for entity in entities:
        entity.draw()
