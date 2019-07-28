from __future__ import annotations

from enum import Enum, auto
from typing import List, TYPE_CHECKING

from bearlibterminal import terminal as blt

if TYPE_CHECKING:
    import tcod.map

    from camera import Camera
    from entity import Entity
    from map_objects.game_map import GameMap


class RenderOrder(Enum):
    CORPSE = 1
    ITEM = auto()
    ACTOR = auto()


def render_all(entities: List[Entity], player: Entity, game_map: GameMap, fov_map: tcod.map.Map, camera: Camera):
    if camera.fov_update:
        # Draw the map
        blt.clear()
        blt.clear_area(x=0, y=0, w=camera.width, h=camera.height)
        game_map.render(fov_map=fov_map, camera=camera)

        # Draw all entities in the list
        entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)
        for entity in entities_in_render_order:
            if camera.in_bounds(entity.position):
                if fov_map.fov[entity.x, entity.y]:
                    point = entity.position - camera.top_left
                    entity.draw(point)

        blt.printf(x=1, y=42, s=f"HP: {player.fighter.hp:02}/{player.fighter.max_hp:02}")

    blt.refresh()
