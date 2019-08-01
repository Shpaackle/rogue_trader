from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

import PIL.Image

from rect import Rect

if TYPE_CHECKING:
    from colors import Colors
    from map_objects import Point


class Panel(Rect):
    def __init__(self, position: Point, width: int, height: int):
        super(Panel, self).__init__(position=position, width=width, height=height)
        elements: defaultdict = defaultdict(list)
        self._bar: PIL.Image = PIL.Image.new("RGBA", (width, height), (255, 255, 255, 0))

    def create_bar(self, width: int, height: int, bar_color: Colors, back_color: Colors) -> PIL.Image:
        bar = self._bar.crop((0, 0, width, height))
        return bar
