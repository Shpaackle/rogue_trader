from enum import Enum

from bearlibterminal import terminal as blt


class Colors(Enum):
    LIGHT_WALL = blt.color_from_argb(0, 130, 100, 50)
    LIGHT_GROUND = blt.color_from_argb(0, 200, 180, 50)
    DARK_WALL = blt.color_from_argb(0, 100, 100, 100)
    DARK_GROUND = blt.color_from_argb(0, 50, 50, 150)
