from __future__ import annotations

from typing import TYPE_CHECKING

import tcod

from colors import Color
from game_states import GameStates
from render_functions import RenderOrder


if TYPE_CHECKING:
    from entity import Entity


def kill_player(player: Entity):
    player.char = "%"
    player.color = Color.RED

    return "You died!", GameStates.PLAYER_DEAD


def kill_monster(monster: Entity):
    death_message = f"{monster.name.capitalize()} is dead!"

    monster.char = "%"
    monster.color = Color.RED
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = f"remains of {monster.name}"
    monster.render_order = RenderOrder.CORPSE

    return death_message

