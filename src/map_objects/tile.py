from map_objects.point import Point


class Tile:
    def __init__(self, x: int, y: int, label: str):
        self._point: Point = Point(x=x, y=y)
        self.label: str = label

    @property
    def x(self):
        return self._point.x

    @x.setter
    def x(self, value: int):
        new_point = Point(x=value, y=self.y)
        self._point = new_point

    @property
    def y(self):
        return self._point.y

    @y.setter
    def y(self, value):
        new_point = Point(x=self.x, y=value)
        self._point = new_point

    @classmethod
    def empty(cls, x: int, y: int):
        return Tile(x=x, y=y, label="EMPTY")

    @classmethod
    def wall(cls, x: int, y: int):
        return Tile(x=x, y=y, label="WALL")

    @classmethod
    def floor(cls, x: int, y: int):
        return Tile(x=x, y=y, label="FLOOR")

    def __str__(self):
        return f"{self.label} {self._point}"

    def __repr__(self):
        return f"({self.__class__.__name__}) x={self.x}, y={self.y}, label={self.label}"
