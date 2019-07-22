import pytest

from map_objects.game_map import GameMap


@pytest.fixture
def my_map():
    return GameMap(width=50, height=50)
