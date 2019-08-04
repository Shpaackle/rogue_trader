from bearlibterminal import terminal as blt

from map_objects.point import Point


def handle_keys(key: int) -> dict:
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

    if key == blt.TK_ESCAPE or key == blt.TK_Q or key == blt.TK_CLOSE:
        return {"exit": True}

    return {}
