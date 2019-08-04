from __future__ import annotations

from typing import List, TYPE_CHECKING

from colors import Colors
from game_messages import Message

if TYPE_CHECKING:
    from entity import Entity


def heal(*args, **kwargs) -> List[dict]:
    entity: Entity = args[0]
    amount: int = kwargs.get("amount")

    results: List[dict] = []

    if entity.fighter.hp == entity.fighter.max_hp:
        results.append({"consumed": False, "message": Message("You are already at full health", Colors.YELLOW)})
    else:
        entity.fighter.heal(amount)
        results.append({"consumed": True, "message": Message("Your wounds start to feel better!", Colors.GREEN)})

    return results
