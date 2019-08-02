from __future__ import annotations

from enum import Enum, auto
from typing import List, TYPE_CHECKING

from bearlibterminal import terminal as blt

from colors import Colors

if TYPE_CHECKING:
    import tcod.map

    from camera import Camera
    from entity import Entity
    from game_messages import MessageLog
    from map_objects.game_map import GameMap
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


class RenderOrder(Enum):
    CORPSE = 1
    ITEM = auto()
    ACTOR = auto()


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

    if bar_width <= 0:
        return

    blt.composition = True
    bk_color = blt.color_from_argb(*back_color.argb)
    bar_color = blt.color_from_argb(*bar_color.argb)

    bar = " " * total_width
    blt.printf(x, y, s=f"[font=bar][bkcolor={bk_color}]{bar}")
    blt.printf(x, y, s=f"[font=bar][bkcolor={bar_color}]{bar[:bar_width]}")

    blt.printf(
        x=int(x + total_width / 2),
        y=y,
        s=f"[font=bar_font][spacing=2x2]{name}: {value:02}/{maximum:02}[/font]",
    )


def render_all(
    entities: List[Entity],
    player: Entity,
    game_map: GameMap,
    fov_map: tcod.map.Map,
    camera: Camera,
    message_log: MessageLog,
    ui_panel: Rect,
    bar_width: int,
):
    if camera.fov_update:
        # Draw the map
        blt.clear()
        # blt.clear_area(x=0, y=0, w=camera.width, h=camera.height)
        game_map.render(fov_map=fov_map, camera=camera)

        # Draw all entities in the list
        entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)
        for entity in entities_in_render_order:
            if camera.in_bounds(entity.position):
                if fov_map.fov[entity.x, entity.y]:
                    point = entity.position - camera.top_left
                    entity.draw(point)

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

    for i, message in enumerate(message_log.messages, 0):
        blt.printf(x=message_log.x, y=ui_panel.y + (i * 2), s=f"[TK_ALIGN_LEFT][color={blt.color_from_argb(*message.color.argb)}][font=ui_font]{message.text}")

    blt.refresh()
