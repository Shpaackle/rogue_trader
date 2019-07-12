from typing import List

from bearlibterminal import terminal as blt

from entity import Entity
from map_objects.game_map import GameMap


def render_all(entities: List[Entity], game_map: GameMap, colors: dict):
    # Draw the map
    game_map.render(colors=colors)

    # Draw all entities in the list
    for entity in entities:
        entity.draw()
