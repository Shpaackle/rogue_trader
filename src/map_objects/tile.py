from __future__ import annotations

from enum import auto, Enum

from colors import Color
from map_objects.point import Point


class TileType(Enum):
    CAVE = auto()
    FLOOR = auto()
    EMPTY = auto()
    WALL = auto()


class Tile:
    def __init__(
        self,
        x: int,
        y: int,
        label: TileType,
        walkable: bool = False,
        transparent: bool = False,
    ):
        self._point: Point = Point(x=x, y=y)
        self.label: TileType = label
        self.walkable: bool = walkable
        self.transparent: bool = transparent
        self._visible: bool = False
        self._explored: bool = False

    @property
    def blocks_sight(self) -> bool:
        return not self.transparent

    @property
    def blocked(self) -> bool:
        return not self.walkable

    @property
    def point(self) -> Point:
        return self._point

    @property
    def explored(self) -> bool:
        return self._explored

    @explored.setter
    def explored(self, value: bool):
        self._explored = value

    @property
    def color(self):
        if self.label == TileType.WALL or self.label == TileType.CAVE:
            label = "WALL"
        else:
            label = "GROUND"

        if self.visible:
            light = "LIGHT"
        else:
            light = "DARK"

        return Color[f"{light}_{label}"].value

    @property
    def char(self) -> str:
        chars = {
            TileType.FLOOR: ".",
            TileType.EMPTY: ".",
            TileType.CAVE: "#",
            TileType.WALL: "#",
        }
        return chars[self.label]

    @property
    def visible(self) -> bool:
        return self._visible

    @visible.setter
    def visible(self, value: bool):
        self._visible = value

    @property
    def x(self) -> int:
        return self._point.x

    @x.setter
    def x(self, value: int):
        new_point = Point(x=value, y=self.y)
        self._point = new_point

    @property
    def y(self) -> int:
        return self._point.y

    @y.setter
    def y(self, value):
        new_point = Point(x=self.x, y=value)
        self._point = new_point

    @classmethod
    def empty(cls, point: Point) -> "Tile":
        return Tile(x=point.x, y=point.y, label=TileType.EMPTY)

    @classmethod
    def wall(cls, point: Point) -> "Tile":
        return Tile(
            x=point.x, y=point.y, label=TileType.WALL, walkable=False, transparent=False
        )

    @classmethod
    def floor(cls, point: Point) -> "Tile":
        return Tile(
            x=point.x, y=point.y, label=TileType.FLOOR, walkable=True, transparent=True
        )

    @classmethod
    def cave(cls, point: Point) -> "Tile":
        return Tile(
            x=point.x, y=point.y, label=TileType.CAVE, walkable=False, transparent=False
        )

    @classmethod
    def from_label(cls, point: Point, label: TileType = TileType.EMPTY) -> "Tile":
        tiles = {
            "CAVE": Tile.cave,
            "FLOOR": Tile.floor,
            "WALL": Tile.wall,
            "EMPTY": Tile.empty,
        }
        tile = tiles[label.name]
        return tile(point)

    @classmethod
    def from_string(cls, point: Point, string: str = "EMPTY") -> "Tile":
        # tiles = {
        #     "CAVE": Tile.cave,
        #     "FLOOR": Tile.floor,
        #     "WALL": Tile.wall,
        #     "EMPTY": Tile.empty
        # }
        # tile = tiles[string]
        return cls.from_label(point, TileType[string])

    def __str__(self):
        return f"{self._point} {self.label}"

    def __repr__(self):
        return f"({self.__class__.__name__}) x={self.x}, y={self.y}, label={self.label}"
