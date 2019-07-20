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

    if key == blt.TK_ESCAPE or key == blt.TK_Q or key == blt.TK_CLOSE:
        return {"exit": True}

    return {}
