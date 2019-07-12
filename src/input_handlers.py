from bearlibterminal import terminal as blt

from map_objects.point import Point


def handle_keys(key: int):
    if key == blt.TK_UP:
        return {"move": Point(0, -1)}
    elif key == blt.TK_DOWN:
        return {"move": Point(0, 1)}
    elif key == blt.TK_LEFT:
        return {"move": Point(-1, 0)}
    elif key == blt.TK_RIGHT:
        return {"move": Point(1, 0)}
    elif key == blt.TK_P:
        return {"redraw": True}
    # elif key == blt.TK_I:
    #     return {"first_step": True}
    # elif key == blt.TK_O:
    #     return {"second_step": True}
    # elif key == blt.TK_A:
    #     return {"map_settings": "first_one_up"}
    # elif key == blt.TK_S:
    #     return {"map_settings": "first_one_down"}
    # elif key == blt.TK_D:
    #     return {"map_settings": "first_two_up"}
    # elif key == blt.TK_F:
    #     return {"map_settings": "first_two_down"}
    # elif key == blt.TK_H:
    #     return {"map_settings": "second_one_up"}
    # elif key == blt.TK_J:
    #     return {"map_settings": "second_one_down"}
    # elif key == blt.TK_K:
    #     return {"map_settings": "second_two_up"}
    # elif key == blt.TK_L:
    #     return {"map_settings": "second_two_down"}
    #

    if key == blt.TK_ESCAPE or key == blt.TK_Q:
        return {"exit": True}

    return {}
