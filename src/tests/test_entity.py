# entity.position
# entity.char
# entity.color
# entity.x
# entity.y
# entity.move

import pytest

from colors import Color
from entity import Entity
from map_objects import Point


@pytest.fixture
def player() -> Entity:
    e: Entity = Entity(position=Point(x=3, y=3), char="@", color=Color.WHITE)
    return e


@pytest.fixture
def goblin() -> Entity:
    e: Entity = Entity(position=Point(x=5, y=5), char="g", color=Color.LIGHT_GREEN)
    return e
