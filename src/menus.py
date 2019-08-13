from __future__ import annotations

import textwrap
from typing import List, TYPE_CHECKING

import tcod
from bearlibterminal import terminal as blt

from constants import CONSTANTS
from map_objects.point import Point
from rect import Rect

if TYPE_CHECKING:
    from camera import Camera
    from components.inventory import Inventory
    from entity import Entity


class Menu(Rect):
    def __init__(
        self,
        position: Point,
        width: int,
        height: int,
        header: List[str] = None,
        options: List[str] = None,
    ):
        super(Menu, self).__init__(position=position, width=width, height=height)
        if header is None:
            self.header: List[str] = []
        else:
            self.header: List[str] = header

        if options is None:
            self.options: List[str] = []
        else:
            self.options: List[str] = []

    @property
    def options_y(self) -> int:
        return self.y + len(self.header) + 1


def menu(
    camera_width: int, header: str, options: List[str], width: int, panel_y: int = None
):
    if len(options) > 26:
        raise ValueError("Cannot have a menu with more than 26 options.")

    # Calculate total height for the header (after auto-wrap) and one line per option
    wrapped_header = textwrap.wrap(text=header, width=width * 2)
    height = len(options) + len(wrapped_header)
    if panel_y is None:
        panel_y = 2
    panel = Menu(
        position=Point(x=2, y=panel_y),
        width=camera_width * 2,
        height=height,
        header=wrapped_header,
        options=options,
    )

    for i, text_line in enumerate(panel.header):
        blt.printf(x=panel.x, y=panel.y + i * 2, s=f"{text_line}")

    letter_index = ord("a")
    for i, option_text in enumerate(options):
        text = f"({chr(letter_index + i)}) {option_text}"
        blt.puts(
            x=panel.x, y=panel.options_y + i * 2, s=f"{text}", align=blt.TK_ALIGN_LEFT
        )


def inventory_menu(
    camera: Camera, header: str, inventory: Inventory, inventory_width: int
):
    # show a menu with each item of the inventory as an option
    if len(inventory.items) == 0:
        options = ["Inventory is empty."]
    else:
        options = [item.name for item in inventory.items]

    menu(
        camera_width=camera.width, header=header, options=options, width=inventory_width
    )


def main_menu(camera_width: int):
    options = ["Play a new game", "Continue last game", "Quit"]

    header = CONSTANTS.window_title + "\n" + "By Shpaackle"

    menu(
        camera_width=camera_width,
        header=header,
        options=options,
        width=CONSTANTS.screen_width,
    )


def level_up_menu(header, player: Entity, menu_width, screen_width, screen_height):
    options = [f"Constitution (+20HP, from {player.fighter.max_hp}",
               f"Strength (+1 attack, from {player.fighter.power}",
               f"Agility (+1 defense, from {player.fighter.defense}"]

    menu(camera_width=menu_width, header=header, options=options, width=screen_width)


def message_box(header: str, width: int, screen_width: int, screen_height: int):
    menu(camera_width=width, header=header, options=[], width=screen_width, panel_y=10)
