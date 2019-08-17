from __future__ import annotations


from map_objects.point import Point
from rect import Rect


class Constants:
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
    ui_panel: Rect = Rect(position=Point(x=0, y=68), width=240, height=24)

    room_min_size: int = 10
    room_max_size: int = 6
    max_rooms: int = 30
    max_monsters: int = 10
    min_monsters: int = 5
    max_items: int = 50

    fov_algorithm: int = 0
    fov_light_walls: bool = True
    fov_radius: int = 10

    player_hp: int = 100
    player_defense: int = 1
    player_power: int = 4

    level_up_base: int = 200
    level_up_factor: int = 150

    @property
    def message_x(self) -> int:
        message_x: int = (self.bar_width + 2) * 2
        return message_x

    @property
    def message_width(self) -> int:
        message_width: int = self.screen_width - ((self.bar_width - 2) * 2)
        return message_width

    @property
    def panel_y(self) -> int:
        panel_y: int = self.screen_height - (self.panel_height * 2)
        return panel_y

    @property
    def message_height(self) -> int:
        panel_height: int = self.panel_height - 1
        return panel_height


CONSTANTS = Constants()
