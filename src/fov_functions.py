from __future__ import annotations

import tcod.map

from map_objects.game_map import GameMap
from map_objects.point import Point
from map_objects.tile import Tile


def initialize_fov(game_map: GameMap):
    fov_map: tcod.map.Map = tcod.map.Map(
        width=game_map.width, height=game_map.height, order="F"
    )

    for tile in game_map.tiles:
        fov_map.walkable[tile.x, tile.y] = tile.walkable
        fov_map.transparent[tile.x, tile.y] = tile.transparent

    return fov_map


def recompute_fov(
    fov_map: tcod.map.Map, point: Point, radius, light_walls=True, algorithm=0
):
    fov_map.compute_fov(
        x=point.x,
        y=point.y,
        radius=radius,
        light_walls=light_walls,
        algorithm=algorithm,
    )
    # tcod.map_compute_fov(fov_map, point.x, point.y, radius, light_walls, algorithm)
