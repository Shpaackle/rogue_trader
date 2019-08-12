from __future__ import annotations

import random
from typing import Iterator, TYPE_CHECKING, Optional

import numpy as np
import tcod
from bearlibterminal import terminal as blt
from tcod.map import Map

from map_objects.point import Point
from map_objects.tile import Tile, TileType
from rect import Rect

if TYPE_CHECKING:
    from camera import Camera

FILLED = 1
EMPTY = 0


class GameMap(tcod.map.Map):
    def __init__(self, width: int, height: int, dungeon_level: int = 1):
        super(GameMap, self).__init__(width=width, height=height, order="F")

        self.cave_map: np.array = np.zeros((width, height), order="F")
        self._explored: np.array = np.full((width, height), order="F", fill_value=False)
        self.tile_map: np.array = np.zeros((width, height), order="F")

        self.dungeon_level: int = dungeon_level

    def is_explored(self, point: Point) -> bool:
        return self._explored[point.x, point.y]

    def explore(self, point: Point) -> None:
        self._explored[point.x, point.y] = True

    @property
    def tiles(self) -> Iterator[Tile]:
        for i in range(self.height):
            for j in range(self.width):
                point = Point(x=j, y=i)
                if self.cave_map[j, i]:
                    label = TileType.CAVE
                else:
                    label = TileType.FLOOR
                tile = Tile.from_label(point=point, label=label)
                yield tile

    def is_blocked(self, point: Point) -> bool:
        if not self.walkable[point.x, point.y]:
            return True

        return False

    def create_room(self, room: Rect):
        for x in range(room.x + 1, room.right):
            for y in range(room.y + 1, room.bottom):
                self.walkable[x, y] = True
                self.transparent[x, y] = True

    def create_h_tunnel(self, x1: int, x2: int, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.walkable[x, y] = True
            self.transparent[x, y] = True

    def create_v_tunnel(self, x: int, y1: int, y2: int):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.walkable[x, y] = True
            self.transparent[x, y] = True

    def in_bounds(self, point: Point) -> bool:
        return 0 <= point.x < self.width and 0 <= point.y < self.height

    def count_neighbors(self, point: Point, steps: int):
        count = 0
        for i in range(-steps, steps):
            for j in range(-steps, steps):
                if abs(i) == 2 and abs(j) == 2:
                    continue

                neighbor = Point(x=point.x + j, y=point.y + i)
                if not self.in_bounds(neighbor):
                    continue
                if self.cave_map[neighbor.x, neighbor.y]:
                    count += 1

        return count

    def count_one_step_neighbors(self, center: Point) -> int:
        # TODO: refactor to make more generic
        # combine with two_step to take a steps parameter and returns multiple values
        count = 0
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                point = Point(x=center.x + j, y=center.y + i)
                if not self.in_bounds(point=point):
                    continue
                if self.cave_map[point.x, point.y]:
                    count += 1

        return count

    # TODO: refactor to make more generic
    def count_two_step_neighbors(self, center: Point) -> int:
        count = 0
        for i in range(-2, 2):
            for j in range(-2, 2):
                if abs(i) == 2 and abs(j) == 2:
                    continue

                point = Point(x=center.x + j, y=center.y + i)
                if not self.in_bounds(point):
                    continue
                if self.cave_map[point.x, point.y]:
                    count += 1

        return count

    def place_tile(self, point: Point, tile: Tile):
        x, y = point
        self.walkable[x, y] = tile.walkable
        self.transparent[x, y] = tile.transparent
        self.tile_map[x, y] = tile.label.value

        if tile.label == TileType.CAVE:
            self.cave_map[x, y] = FILLED
        elif tile.label == TileType.FLOOR:
            self.cave_map[x, y] = EMPTY

    def get_tile(self, point: Point, fov_map: tcod.map.Map) -> Optional[Tile]:
        if not self.in_bounds(point):
            return None

        label = TileType(self.tile_map[point.x, point.y])
        tile = Tile.from_label(point=point, label=label)
        tile.visible = fov_map.fov[point.x, point.y]
        return tile

    def render(self, fov_map: tcod.map.Map, camera: Camera):
        for row, y in enumerate(range(camera.top, camera.bottom)):
            for col, x in enumerate(range(camera.left, camera.right)):
                point = Point(x, y)
                if not self.in_bounds(point):
                    continue

                tile = self.get_tile(point, fov_map=fov_map)
                tile.visible = fov_map.fov[x, y]
                if tile.visible:
                    self.explore(point)
                tile.explored = self.is_explored(point)

                if tile.explored:
                    blt.printf(
                        x=col * 2,
                        y=row * 2,
                        s=f"[font=map][color={tile.color}]{tile.char}[/color][/font]",
                    )

    def to_json(self) -> dict:
        json_data = {
            "width": self.width,
            "height": self.height,
            "explored": self._explored.tolist(),
            "tile_map": self.tile_map.tolist(),
            "dungeon_level": self.dungeon_level
        }

        return json_data

    @classmethod
    def from_json(cls, json_data) -> GameMap:
        game_map = cls(width=json_data["width"], height=json_data["height"])

        for i in range(game_map.height):
            for j in range(game_map.width):
                point = Point(x=j, y=i)
                label = TileType(int(json_data["tile_map"][j][i]))
                tile = Tile.from_label(point=point, label=label)
                game_map.place_tile(point=point, tile=tile)
                if json_data["explored"][j][i]:
                    game_map.explore(point)

        game_map.dungeon_level = json_data["dungeon_level"]

        return game_map
