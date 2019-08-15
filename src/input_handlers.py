from __future__ import annotations

from typing import Dict, Optional

from bearlibterminal import terminal as blt

from game_states import GameStates
from map_objects.point import Point


def handle_keys(key: int, game_state: GameStates) -> dict:
    if game_state == GameStates.PLAYER_TURN:
        return handle_player_turn_keys(key=key)
    elif game_state == GameStates.PLAYER_DEAD:
        return handle_player_dead_keys(key=key)
    elif game_state == GameStates.TARGETING:
        return handle_targeting_keys(key=key)
    elif game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        return handle_inventory_keys(key=key)
    elif game_state == GameStates.LEVEL_UP:
        return handle_level_up_menu(key=key)
    elif game_state == GameStates.CHARACTER_SCREEN:
        return handle_character_screen(key=key)

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
    elif key == blt.TK_Z:
        return {"wait": True}

    elif key == blt.TK_G:
        return {"pickup": True}

    elif key == blt.TK_I:
        return {"show_inventory": True}

    elif key == blt.TK_D:
        return {"drop_inventory": True}

    elif key == blt.TK_ENTER:
        return {"take_stairs": True}

    elif key == blt.TK_C:
        return {"show_character_screen": True}

    if key in {blt.TK_ESCAPE, blt.TK_Q, blt.TK_CLOSE}:
        return {"exit": True}

    return {}


def handle_targeting_keys(key: int) -> Dict[str, bool]:
    if key == blt.TK_ESCAPE:
        return {"exit": True}

    return {}


def handle_player_dead_keys(key: int) -> Dict[str, bool]:
    if key == blt.TK_I:
        return {"show_inventory": True}

    if key == blt.TK_ESCAPE:
        return {"exit": True}

    return {}


def handle_inventory_keys(key: int) -> dict:
    if key == blt.TK_ESCAPE:
        return {"exit": True}

    index = key - blt.TK_A
    if index >= 0:
        return {"inventory_index": index}

    return {}


def handle_main_menu(key: int) -> Dict[str, bool]:
    if key == blt.TK_A:
        print("returned new_game")
        return {"new_game": True}
    elif key == blt.TK_B:
        print("returned load_game")
        return {"load_game": True}
    elif key in {blt.TK_C, blt.TK_ESCAPE, blt.TK_CLOSE}:
        print("returned exit_game")
        return {"exit_game": True}

    return {}


def handle_level_up_menu(key: int) -> dict:
    if key == blt.TK_A:
        return {"level_up": "hp"}
    elif key == blt.TK_B:
        return {"level_up": "str"}
    elif key == blt.TK_C:
        return {"level_up": "dex"}

    return {}


def handle_character_screen(key: int) -> dict:
    if key == blt.TK_ESCAPE:
        return {"exit": True}

    return {}


def handle_mouse(key: int) -> Dict[str, Point]:
    mouse_position: Point = Point(
        x=blt.state(blt.TK_MOUSE_X) // 2, y=blt.state(blt.TK_MOUSE_Y) // 2
    )

    if key == blt.TK_MOUSE_LEFT:
        return {"left_click": mouse_position}
    elif key == blt.TK_MOUSE_RIGHT:
        return {"right_click": mouse_position}

    return {}

