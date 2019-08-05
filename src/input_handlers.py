from bearlibterminal import terminal as blt

from game_states import GameStates
from map_objects.point import Point


def handle_keys(key: int, game_state: GameStates) -> dict:
    if game_state == GameStates.PLAYER_TURN:
        return handle_player_turn_keys(key=key)
    elif game_state == GameStates.PLAYER_DEAD:
        return handle_player_dead_keys(key=key)
    elif game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        return handle_inventory_keys(key=key)

    return {}


def handle_player_turn_keys(key: int) -> dict:
    if key == blt.TK_UP or key == blt.TK_K:
        return {"move": Point(0, -1)}
    elif key == blt.TK_DOWN or key == blt.TK_J:
        return {"move": Point(0, 1)}
    elif key == blt.TK_LEFT or key == blt.TK_H:
        return {"move": Point(-1, 0)}
    elif key == blt.TK_RIGHT or key == blt.TK_L:
        return {"move": Point(1, 0)}
    elif key == blt.TK_Y:
        return {"move": Point(-1, -1)}
    elif key == blt.TK_U:
        return {"move": Point(1, -1)}
    elif key == blt.TK_B:
        return {"move": Point(-1, 1)}
    elif key == blt.TK_N:
        return {"move": Point(1, 1)}

    elif key == blt.TK_G:
        return {"pickup": True}

    elif key == blt.TK_I:
        return {"show_inventory": True}

    elif key == blt.TK_D:
        return {"drop_inventory": True}

    if key == blt.TK_ESCAPE or key == blt.TK_Q or key == blt.TK_CLOSE:
        return {"exit": True}

    return {}


def handle_player_dead_keys(key: int) -> dict:
    if key == blt.TK_I:
        return {"show_inventory": True}

    if key == blt.TK_ESCAPE:
        return {"exit": True}

    return {}


def handle_inventory_keys(key: int) -> dict:
    index = key - blt.TK_A
    print(f"index = {index}")

    if key == blt.TK_ESCAPE:
        return {"exit": True}

    if index >= 0:
        return {"inventory_index": index}

    return {}
