from __future__ import annotations

import math
from collections import namedtuple
from dataclasses import dataclass
from enum import Enum
from typing import Generator, Iterator


POINT = namedtuple("POINT", ["x", "y"],)


class Direction(Enum):
    NW = POINT(-1, 1)
    N = POINT(0, 1)
    NE = POINT(1, 1)
    W = POINT(-1, 0)
    E = POINT(1, 0)
    SW = POINT(-1, -1)
    S = POINT(0, -1)
    SE = POINT(1, -1)
    ORIGIN = POINT(0, 0)


@dataclass(init=True, repr=True, eq=True, order=False, frozen=True)
class Point:
    """
    A simple container to represent a single point in the map's grid
    added functionality for adding, subtracting, or comparing equality of two points
    can be iterated to get x- and y-coordinates

    Args:
        x- and y-coordinate for the point
    """
    x: int
    y: int

    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Point") -> "Point":
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, other: int) -> "Point":
        return Point(self.x * other, self.y * other)

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __iter__(self) -> Iterator[int]:
        yield self.x
        yield self.y

    @property
    def NW(self) -> "Point":
        return self._direction(Direction.NW.value)

    @property
    def N(self) -> "Point":
        return self._direction(Direction.N.value)

    @property
    def NE(self) -> "Point":
        return self._direction(Direction.NE.value)

    @property
    def W(self) -> "Point":
        return self._direction(Direction.W.value)

    @property
    def E(self) -> "Point":
        return self._direction(Direction.E.value)

    @property
    def SW(self) -> "Point":
        return self._direction(Direction.SW.value)

    @property
    def S(self) -> "Point":
        return self._direction(Direction.S.value)

    @property
    def SE(self) -> "Point":
        return self._direction(Direction.SE.value)

    @property
    def ORIGIN(self) -> "Point":
        return self._direction(Direction.ORIGIN.value)

    def _direction(self, point) -> "Point":
        return Point(self.x + point.x, self.y + point.y)

    # def distance(self, point):
    #     return Point(abs(self.x - point.x), abs(self.y - point.y))

    @property
    def all_neighbors(self) -> Generator[Point]:
        for direction in [self.N, self.NE, self.E, self.SE, self.S, self.SW, self.W, self.NW]:
            yield direction

    @property
    def direct_neighbors(self) -> Point:
        for direction in [self.N, self.E, self.S, self.W]:
            yield direction

    def distance_to(self, p2) -> float:
        x, y = self - p2
        return math.sqrt(x ** 2 + y ** 2)
