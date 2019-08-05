from __future__ import annotations

from map_objects import Point
from rect import Rect


def get_constants() -> dict:
    screen_width: int = 120 * 2
    screen_height: int = 45 * 2
    window_title: str = "Rogue Trader"

    map_font: str = "map font: mplus-1p-bold.ttf, size=12, spacing=2x2"
    ui_font: str = "ui_font font: mplus-1p-bold.ttf, size=10"
    bar_font: str = "bar font: mplus-1p-bold.ttf, size=6, spacing=2x2"
    hover_font: str = "hover font: mplus-1p-bold.ttf, size=6"

    map_width: int = 80
    map_height: int = 80
    camera_width: int = 65
    camera_height: int = 33

    bar_width: int = 20
    panel_height: int = 12
    panel_y: int = screen_height - (panel_height * 2)
    ui_panel: Rect = Rect(position=Point(x=0, y=panel_y), width=screen_width, height=panel_height * 2)

    message_x: int = (bar_width + 2) * 2
    message_width: int = screen_width - ((bar_width - 2) * 2)
    message_height: int = (panel_height - 1)

    room_min_size: int = 10
    room_max_size: int = 6
    max_rooms: int = 30
    max_monsters: int = 10
    min_monsters: int = 5
    max_items: int = 50

    fov_algorithm: int = 0
    fov_light_walls: bool = True
    fov_radius: int = 10

    constants = {
        "screen_width": screen_width,
        "screen_height": screen_height,
        "window_title": window_title,
        "map_font": map_font,
        "ui_font": ui_font,
        "bar_font": bar_font,
        "hover_font": hover_font,
        "map_width": map_width,
        "map_height": map_height,
        "camera_width": camera_width,
        "camera_height": camera_height,
        "bar_width": bar_width,
        "panel_height": panel_height,
        "panel_y": panel_y,
        "ui_panel": ui_panel,
        "message_x": message_x,
        "message_width": message_width,
        "message_height": message_height,
        "room_min_size": room_min_size,
        "room_max_size": room_max_size,
        "max_rooms": max_rooms,
        "max_monsters": max_monsters,
        "min_monsters": min_monsters,
        "max_items": max_items,
        "fov_algorithm": fov_algorithm,
        "fov_light_walls": fov_light_walls,
        "fov_radius": fov_radius,
    }
    return constants
