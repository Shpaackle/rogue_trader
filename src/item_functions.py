from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from colors import Colors
from components.ai import ConfusedMonster
from game_messages import Message

if TYPE_CHECKING:
    import tcod.map

    from entity import Entity
    from map_objects import Point


def heal(*args, **kwargs) -> List[dict]:
    entity: Entity = args[0]
    amount: int = kwargs.get("amount")

    results: List[dict] = []

    if entity.fighter.hp == entity.fighter.max_hp:
        results.append(
            {
                "consumed": False,
                "message": Message("You are already at full health", Colors.YELLOW),
            }
        )
    else:
        entity.fighter.heal(amount)
        results.append(
            {
                "consumed": True,
                "message": Message("Your wounds start to feel better!", Colors.GREEN),
            }
        )

    return results


def cast_lightning(*args, **kwargs) -> List[dict]:
    caster: Entity = args[0]
    entities: List[Entity] = kwargs.get("entities")
    fov_map: tcod.map.Map = kwargs.get("fov_map")
    damage: int = kwargs.get("damage")
    maximum_range: int = kwargs.get("maximum_range")

    results: List[dict] = []

    target: Optional[Entity] = None
    closest_distance = maximum_range + 1

    for entity in entities:
        if entity.fighter and entity != caster and fov_map.fov[entity.x, entity.y]:
            distance: float = caster.distance_to(entity.position)

            if distance < closest_distance:
                target: Entity = entity
                closest_distance = distance

    if target:
        results.append(
            {
                "consumed": True,
                "target": target,
                "message": Message(
                    f"A lightning bolt strikes the {target.name} with a loud thunder! The damage is {damage}"
                ),
            }
        )
        results.extend(target.fighter.take_damage(damage))
    else:
        results.append(
            {
                "consumed": False,
                "target": None,
                "message": Message("No enemy is close enough to strike.", Colors.RED),
            }
        )

    return results


def cast_fireball(*args, **kwargs) -> List[dict]:
    entities: Optional[List[Entity]] = kwargs.get("entities")
    fov_map: Optional[tcod.map.Map] = kwargs.get("fov_map")
    damage: Optional[int] = kwargs.get("damage")
    radius: Optional[int] = kwargs.get("radius")
    target_position: Optional[Point] = kwargs.get("target_position")

    results = []

    if not fov_map.fov[target_position.x, target_position.y]:
        results.append(
            {
                "consumed": False,
                "message": Message(
                    "You cannot target a tile outside of your field of view.",
                    Colors.YELLOW,
                ),
            }
        )
        return results

    results.append(
        {
            "consumed": True,
            "message": Message(
                f"The fireball explodes, burning everything within {radius} tiles!",
                Colors.ORANGE,
            ),
        }
    )

    for entity in entities:
        if entity.distance_to(target_position) <= radius and entity.fighter:
            results.append(
                {
                    "message": Message(
                        f"The {entity.name} gets burned for {damage} hit points."
                    )
                }
            )
            results.extend(entity.fighter.take_damage(damage))

    return results


def cast_confuse(*args, **kwargs) -> List[dict]:
    entities: Optional[List[Entity]] = kwargs.get("entities")
    fov_map: Optional[tcod.map.Map] = kwargs.get("fov_map")
    target_position: Optional[Point] = kwargs.get("target_position")

    results = []

    if not fov_map.fov[target_position.x, target_position.y]:
        results.append(
            {
                "consumed": False,
                "message": Message(
                    "You cannot target a tile outside your field of view.",
                    Colors.YELLOW,
                ),
            }
        )
        return results

    for entity in entities:
        if entity.position == target_position and entity.ai:
            confused_ai = ConfusedMonster(entity.ai, 10)

            confused_ai.owner = entity
            entity.ai = confused_ai

            results.append(
                {
                    "consumed": True,
                    "message": Message(
                        f"The eyes of the {entity.name} look vacant, as they start to stumble around!",
                        Colors.LIGHT_GREEN,
                    ),
                }
            )

            break

    else:
        results.append(
            {
                "consumed": False,
                "message": Message(
                    f"There is no enemy to target at that location.", Colors.YELLOW
                ),
            }
        )

    return results
