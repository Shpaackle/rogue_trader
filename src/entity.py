from typing import List, Optional

from bearlibterminal import terminal as blt

from colors import Color
from map_objects.point import Point


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    def __init__(self, position: Point, char: str, color: Color, name: str, blocks: bool = False):
        self.position: Point = position
        self.char: str = char
        self.color: Color = color
        self.name: str = name
        self.blocks: bool = blocks

    @property
    def x(self) -> int:
        return self.position.x

    @x.setter
    def x(self, value: int):
        self.position = Point(value, self.y)

    @property
    def y(self) -> int:
        return self.position.y

    @y.setter
    def y(self, value):
        self.position = Point(self.x, value)

    def move(self, point: Point):
        """ Move the entity in a particular direction """
        self.position += point

    def draw(self):
        """ Draw the entity to the terminal """
        blt.printf(x=self.x, y=self.y, s=f"[color={self.color.value}]{self.char}[/color]")


def get_blocking_entities_at_location(entities: List[Entity], destination: Point) -> Optional[Entity]:
    for entity in entities:
        if entity.blocks and entity.position == destination:
            return entity

    return None
