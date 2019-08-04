from __future__ import annotations

from map_objects.point import Point


class Rect:
    def __init__(self, position: Point, width: int, height: int):
        self.position: Point = position
        self.width: int = width
        self.height: int = height

    def __iter__(self):
        for j in range(self.height):
            for i in range(self.width):
                yield Point(x=self.x + i, y=self.y + j)

    @property
    def x(self) -> int:
        return self.position.x

    @x.setter
    def x(self, value: int) -> None:
        new_position = Point(value, self.y)
        self.position = new_position

    @property
    def y(self) -> int:
        return self.position.y

    @y.setter
    def y(self, value: int) -> None:
        new_position = Point(self.x, value)
        self.position = new_position

    @property
    def center(self) -> Point:
        x = self.x + self.width // 2
        y = self.y + self.height // 2
        return Point(x, y)

    @center.setter
    def center(self, point: Point) -> None:
        x = point.x - self.width // 2
        y = point.y - self.height // 2
        self.position = Point(x, y)

    @property
    def left(self) -> int:
        return self.x

    @property
    def right(self) -> int:
        return self.x + (self.width - 1)

    @property
    def top(self) -> int:
        return self.y

    @property
    def bottom(self) -> int:
        return self.y + (self.height - 1)

    @property
    def top_left(self) -> Point:
        return self.position

    @top_left.setter
    def top_left(self, value: Point) -> None:
        if self.top_left != value:
            self.position = value

    def intersect(self, other: "Rect") -> bool:
        """ Return True if this rectangle intersects with another one """
        return (
            self.x <= other.right
            and self.right >= other.x
            and self.y <= other.bottom
            and self.bottom >= other.y
        )

    def in_bounds(self, point: Point) -> bool:
        return self.left <= point.x < self.right and self.top <= point.y < self.bottom

    @classmethod
    def from_center(cls, center: Point, width: int, height: int):
        width_offset = (width + 1) // 2 - 1
        height_offset = (height + 1) // 2 - 1

        top_left = Point(center.x - width_offset, center.y - height_offset)

        return Rect(position=top_left, width=width, height=height)
