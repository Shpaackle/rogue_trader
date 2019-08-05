from __future__ import annotations

from typing import TYPE_CHECKING

from colors import Colors
from game_messages import Message
from render_functions import RenderOrder

if TYPE_CHECKING:
    from entity import Entity


def kill_player(player: Entity):
    player.char = "%"
    player.color = Colors.RED

    return Message("You died!", Colors.RED)


def kill_monster(monster: Entity):
    death_message = Message(f"{monster.name.capitalize()} is dead!", Colors.ORANGE)

    monster.char = "%"
    monster.color = Colors.RED
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = f"remains of {monster.name}"
    monster.render_order = RenderOrder.CORPSE

    return death_message

