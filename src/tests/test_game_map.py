import pytest

from map_objects.game_map import GameMap


@pytest.fixture
def game_map() -> GameMap:
    return GameMap(width=50, height=50)


@pytest.fixture
def neighbor_map() -> GameMap:
    game_map: GameMap = GameMap(width=20, height=11)

    """
    01234567890123456789
    .XXX.X...XXX.....XXX
    XX.XX..X..XX.....XXX
    .XXX.X...XXX.....XXX
    XXXXXXXXXXXXXXXXXXXX
    XXXXXXXXXXXXXXXXXXXX
    XXXXXXXXXXXXXXXXXXXX
    XXXXXXXXXXXXXXXXXXXX
    XXXXXXXXXXXXXXXXXXXX
    XXXXXXX.XXX.XXXXXXXX
    XXXXXXXXX.XXXXXXXXXX
    XXXXXXX.XXX.XXXXXXXX
    """

    return game_map


def test_count_neighbors():
    game_map.cave_map[4:10, 5] = 1
    game_map.cave_map[4:10, 7] = 1

    pass


# game_map.explore(point)
# game_map.tiles
# game_map.is_blocked(point)
# game_map.create_room(room)
# game_map.in_bounds(point)
# game_map.count_neighbors(point, steps)
# game_map.place_tile(point, tile)
