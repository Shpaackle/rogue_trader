from bearlibterminal import terminal as blt


def handle_keys(key: int):
    if key == blt.TK_UP or key == blt.TK_W:
        return {"move": (0, -1)}
    elif key == blt.TK_DOWN or key == blt.TK_S:
        return {"move": (0, 1)}
    elif key == blt.TK_LEFT or key == blt.TK_A:
        return {"move": (-1, 0)}
    elif key == blt.TK_RIGHT or key == blt.TK_D:
        return {"move": (1, 0)}

    if key == blt.TK_ESCAPE or key == blt.TK_Q:
        return {"exit": True}

    return {}
