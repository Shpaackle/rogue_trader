from map_objects.point import Point


class Rect:
    def __init__(self, position: Point, width: int, height: int):
        self.position = position
        self.width = width
        self.height = height

    def __iter__(self):
        for j in range(self.height):
            for i in range(self.width):
                yield Point(x=self.x + i, y=self.y + j)

    @property
    def x(self) -> int:
        return self.position.x

    @x.setter
    def x(self, value: int):
        new_position = Point(value, self.y)
        self.position = new_position

    @property
    def y(self) -> int:
        return self.position.y

    @y.setter
    def y(self, value: int):
        new_position = Point(self.x, value)
        self.position = new_position

    @property
    def center(self) -> Point:
        x = self.x + self.width // 2
        y = self.y + self.height // 2
        return Point(x, y)

    @center.setter
    def center(self, point: Point):
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

    def intersect(self, other: "Rect"):
        """ Return True if this rectangle intersects with another one """
        return (
            self.x <= other.right
            and self.right >= other.x
            and self.y <= other.bottom
            and self.bottom >= other.y
        )
