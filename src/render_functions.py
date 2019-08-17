from __future__ import annotations

from enum import Enum, auto
from typing import List, TYPE_CHECKING

from bearlibterminal import terminal as blt

from colors import Colors
from game_states import GameStates
from map_objects.point import Point
from menus import character_screen, inventory_menu, level_up_menu

if TYPE_CHECKING:
    import tcod.map

    from camera import Camera
    from entity import Entity
    from game_messages import MessageLog
    from game_states import GameStates
    from map_objects import GameMap
    from rect import Rect


LINE_STYLE = {
    "T": "─",
    "B": "─",
    "L": "│",
    "R": "│",
    "TL": "┌",
    "TR": "┐",
    "BL": "└",
    "BR": "┘",
}


class RenderLayer(Enum):
    STAIRS = auto()
    CORPSE = auto()
    ITEM = auto()
    ACTOR = auto()


def get_names_under_mouse(
    mouse_position: Point, entities: List[Entity], fov_map: tcod.map.Map, camera: Camera
) -> str:
    if not (
        0 <= mouse_position.x < camera.width - 1
        and 0 <= mouse_position.y < camera.height
    ):
        return ""

    map_point = camera.map_point(mouse_position)
    # blt.printf((camera.width + 1) * 2, 2, f"Map Point = {map_point}")

    names = [
        entity.name
        for entity in entities
        if entity.position == map_point and fov_map.fov[entity.x, entity.y]
    ]
    names = ", ".join(names)

    return names.capitalize()


def render_bar(
    x: int,
    y: int,
    total_width: int,
    name: str,
    value: int,
    maximum: int,
    bar_color: Colors,
    back_color: Colors,
):
    bar_width = int(float(value) / maximum * total_width)

    blt.composition = True
    bk_color = blt.color_from_argb(*back_color.argb)
    bar_color = blt.color_from_argb(*bar_color.argb)
    bar_text = format(
        f"[font=bar_font][spacing=2x2]{name}: {value:02}/{maximum:02}[/font]",
        f"^{total_width}",
    )

    bar = " " * total_width
    blt.printf(x, y, s=f"[font=bar][bkcolor={bk_color}]{bar}")
    blt.printf(x, y, s=f"[font=bar][bkcolor={bar_color}]{bar[:bar_width]}")

    blt.puts(x=int(x + total_width / 2), y=y, s=bar_text, align=blt.TK_ALIGN_CENTER)


def render_all(
    entities: List[Entity],
    player: Entity,
    game_map: GameMap,
    fov_map: tcod.map.Map,
    camera: Camera,
    message_log: MessageLog,
    ui_panel: Rect,
    bar_width: int,
    mouse_position: Point,
    game_state: GameStates,
):

    # Draw the map
    blt.clear()
    # blt.clear_area(x=0, y=0, w=camera.width, h=camera.height)
    blt.layer(0)
    game_map.render(fov_map=fov_map, camera=camera)

    # Draw all entities in the list
    # entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)
    for entity in entities:
        if camera.in_bounds(entity.position):
            if fov_map.fov[entity.x, entity.y] or (entity.stairs and game_map.is_explored(entity.position)):
                point = entity.position - camera.top_left
                entity.draw(point)

    blt.layer(0)
    render_bar(
        x=ui_panel.x,
        y=ui_panel.y,
        total_width=bar_width,
        name="HP",
        value=player.fighter.hp,
        maximum=player.fighter.max_hp,
        bar_color=Colors.RED,
        back_color=Colors.DARK_RED,
    )

    blt.printf(ui_panel.x, ui_panel.y + 2, s=f"Dungeon level: {game_map.dungeon_level}")

    names = get_names_under_mouse(
        mouse_position=mouse_position, entities=entities, fov_map=fov_map, camera=camera
    )
    color = blt.color_from_argb(*Colors.LIGHT_GRAY.argb)
    blt.printf(ui_panel.x, ui_panel.y + 4, s=f"[color={color}]{names}")

    for i, message in enumerate(message_log.messages, 0):
        color = blt.color_from_argb(*message.color.argb)
        blt.printf(
            x=message_log.x,
            y=ui_panel.y + (i * 2),
            s=f"[color={color}]{message.text}",
        )

    fg_color = blt.color_from_argb(*Colors.RED.argb)
    bk_color = blt.color_from_argb(*Colors.YELLOW.argb)
    blt.printf(camera.width * 2 + 2, 4, f"[color={fg_color}]A[/color][+][color={bk_color}][U+2588][/color]")
    # map_point = Point(x=abs(mouse_position.x - camera.center.x), y=abs(mouse_position.y - camera.center.y))
    # blt.printf(camera.width * 2 + 2, 6, f"Map point: {map_point}")
    # blt.printf((camera.width + 1) * 2, 8, f"Player position: {player.position}")

    # blt.printf(ui_panel.x + 1, ui_panel.y + 6, "This is a test!", blt.TK_ALIGN_CENTER)

    if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        if game_state == GameStates.SHOW_INVENTORY:
            inventory_title = (
                "Press the key next to an item to use it, or Esc to cancel. \n"
            )
        else:
            inventory_title = (
                "Press the key next to an item to drop it, or Esc to cancel. \n"
            )
        inventory_menu(
            camera=camera,
            header=inventory_title,
            inventory=player.inventory,
            inventory_width=50,
        )

    elif game_state == GameStates.LEVEL_UP:
        level_up_menu(header="Level up! Choose a stat to raise:", player=player, menu_width=camera.width, screen_width=camera.width, screen_height=camera.height)

    elif game_state == GameStates.CHARACTER_SCREEN:
        character_screen(player, 30, 10, screen_width=camera.width, screen_height=camera.height)

    blt.refresh()
