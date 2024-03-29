from __future__ import annotations

from collections import namedtuple
from enum import Enum


COLOR = namedtuple("Color", ["r", "g", "b", "a"])


class Colors(Enum):
    LIGHT_WALL = COLOR(r=130, g=110, b=50, a=0)
    LIGHT_GROUND = COLOR(r=200, g=180, b=50, a=0)
    DARK_WALL = COLOR(r=0, g=0, b=100, a=0)
    DARK_GROUND = COLOR(r=50, g=50, b=150, a=0)
    WHITE = COLOR(r=255, g=255, b=255, a=0)
    BLACK = COLOR(r=0, g=0, b=0, a=0)
    LIGHT_GREEN = COLOR(r=64, g=128, b=64, a=0)
    DARKER_GREEN = COLOR(r=0, g=128, b=0, a=0)
    RED = COLOR(r=255, g=0, b=0, a=0)
    BLUE = COLOR(r=0, g=0, b=50, a=0)
    DARK_RED = COLOR(r=128, g=0, b=0, a=0)
    ORANGE = COLOR(r=255, g=127, b=0, a=0)
    LIGHT_GRAY = COLOR(r=159, g=159, b=159, a=0)
    VIOLET = COLOR(r=127, g=0, b=255, a=0)
    YELLOW = COLOR(r=255, g=255, b=0, a=0)
    GREEN = COLOR(r=0, g=255, b=0, a=0)
    CYAN = COLOR(r=0, g=255, b=255, a=0)
    LIGHT_CYAN = COLOR(r=115, g=255, b=255, a=0)
    LIGHT_PINK = COLOR(r=255, g=115, b=185, a=0)
    LIGHT_VIOLET = COLOR(r=185, g=115, b=255, a=0)
    DARK_GREY = COLOR(r=95, g=95, b=95, a=0)
    SKY = COLOR(r=0, g=191, b=255, a=0)
    DARKER_ORANGE = COLOR(r=128, g=64, b=0, a=0)

    @property
    def red(self):
        return self.value.r

    @property
    def blue(self):
        return self.value.b

    @property
    def green(self):
        return self.value.g

    @property
    def alpha(self):
        return self.value.a

    @property
    def argb(self):
        return self.alpha, self.red, self.green, self.blue
