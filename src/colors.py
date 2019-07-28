from __future__ import annotations

from enum import Enum

from bearlibterminal import terminal as blt


class Color(Enum):
    LIGHT_WALL = blt.color_from_argb(0, 130, 110, 50)
    LIGHT_GROUND = blt.color_from_argb(0, 200, 180, 50)
    DARK_WALL = blt.color_from_argb(0, 0, 0, 100)
    DARK_GROUND = blt.color_from_argb(0, 50, 50, 150)
    WHITE = blt.color_from_argb(0, 255, 255, 255)
    BLACK = blt.color_from_argb(0, 0, 0, 0)
    LIGHT_GREEN = blt.color_from_argb(0, 64, 128, 64)
    DARKER_GREEN = blt.color_from_argb(0, 0, 128, 0)
    RED = blt.color_from_argb(0, 255, 0, 0)
    BLUE = blt.color_from_argb(0, 0, 0, 255)
