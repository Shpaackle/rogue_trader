from typing import List

import tcod.map
from bearlibterminal import terminal as blt

from entity import Entity
from map_objects.game_map import GameMap


def render_all(entities: List[Entity], game_map: GameMap, fov_map: tcod.map.Map, fov_update: bool, colors: dict):
    if fov_update:
        # Draw the map
        blt.clear()
        game_map.render(fov_map)

        # Draw all entities in the list
        for entity in entities:
            if fov_map.fov[entity.x, entity.y]:
                entity.draw()

    blt.refresh()