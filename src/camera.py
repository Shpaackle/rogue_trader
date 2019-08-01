from __future__ import annotations

from collections import namedtuple
from typing import Iterator, List, TYPE_CHECKING, Set

from bearlibterminal import terminal as blt

from map_objects import Point
from rect import Rect
from ui.panel import Panel

if TYPE_CHECKING:
    import tcod.map

    from entity import Entity
    from map_objects.game_map import GameMap
    from map_objects.tile import Tile


CAMERA_WIDTH = 80
CAMERA_HEIGHT = 40


class Camera(Rect):
    def __init__(self, player: Entity, width: int = None, height: int = None):
        if width is None:
            width: int = CAMERA_WIDTH
        if height is None:
            height: int = CAMERA_HEIGHT

        super(Camera, self).__init__(position=Point(0, 0), width=width, height=height)
        self.center = player.position
        self.player: Entity = player
        self._fov_update: bool = True
        self.ui_panel: Panel = Panel(position=Point(0, 0), width=width, height=height-5)

    def __iter__(self) -> Iterator["camera_view"]:
        camera_view = namedtuple("camera_view", ["x", "y", "map_point"])
        for i in range(self.height):
            for j in range(self.width):
                view = camera_view(x=j, y=i, map_point=Point(x=self.x + j, y=self.y + i))
                yield view

    @property
    def points(self) -> Set[Point]:
        points: Set[Point] = set()
        for i in range(self.height):
            for j in range(self.width):
                point: Point = Point(x=j, y=i)
                points.add(point)
        return points

    @property
    def map_points(self) -> Set[Point]:
        return {Point(x=j, y=i) for i in range(self.top, self.bottom + 1) for j in range(self.left, self.right + 1)}

    def recenter(self) -> None:
        """ Centers camera on point provided"""
        self.center = self.player.position
        self.fov_update = True

    @property
    def fov_update(self) -> bool:
        return self._fov_update

    @fov_update.setter
    def fov_update(self, value: bool):
        self._fov_update = value

    @property
    def camera_view(self):
        view_point = namedtuple("view_point", ["x", "y", "map_point"])
        for row, i in enumerate(range(self.top, self.bottom)):
            for col, j in enumerate(range(self.left, self.right)):
                yield view_point(x=col, y=row, map_point=Point(x=j, y=i))

    def render_view(self, game_map: GameMap, fov_map: tcod.map.Map, entities: List[Entity]):
        for view in self.camera_view:
            tile: Tile = game_map.get_tile(point=view.map_point, fov_map=fov_map)

            if tile is None:
                continue

            blt.printf(x=view.x, y=view.y, s=f"[color={tile.color}]{tile.char}[/color]")

        for entity in entities:
            if self.in_bounds(entity.position):
                if fov_map.fov[entity.x, entity.y]:
                    point = entity.position - self.top_left
                    entity.draw(point)
