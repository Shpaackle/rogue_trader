import pytest

from map_objects.point import Point
from map_objects.tile import Tile, TileType


@pytest.fixture
def zeros():
    return Point(0, 0)


@pytest.fixture
def wall(zeros):
    return Tile.wall(zeros)


@pytest.fixture
def empty(zeros):
    return Tile.empty(zeros)


@pytest.fixture
def floor(zeros):
    return Tile.floor(zeros)


@pytest.fixture
def cave(zeros):
    return Tile.cave(zeros)


# tile.point
# tile.explored
# tile.color
# tile.char
# tile.visible
# tile.x
# tile.y
# tile.empty, wall, floor, cave


def test_tile_from_label(zeros, wall, empty, cave, floor):
    assert wall == Tile.from_label(point=zeros, label=TileType.WALL)
    assert empty == Tile.from_label(point=zeros, label=TileType.EMPTY)
    assert cave == Tile.from_label(point=zeros, label=TileType.CAVE)
    assert floor == Tile.from_label(point=zeros, label=TileType.FLOOR)


def test_tile_from_string(zeros, wall, empty, cave, floor):
    assert wall == Tile.from_string(point=zeros, string="WALL")
    assert empty == Tile.from_string(point=zeros, string="EMPTY")
    assert cave == Tile.from_string(point=zeros, string="CAVE")
    assert floor == Tile.from_string(point=zeros, string="FLOOR")
