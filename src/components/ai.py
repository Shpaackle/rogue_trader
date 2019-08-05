from __future__ import annotations

import random
from typing import List, TYPE_CHECKING

from colors import Colors
from components.entity_component import EntityComponent
from game_messages import Message
from map_objects.point import Point

if TYPE_CHECKING:
    import tcod.map
    from entity import Entity
    from map_objects.game_map import GameMap


class AI(EntityComponent):
    def take_turn(
        self,
        target: Entity,
        fov_map: tcod.map.Map,
        game_map: GameMap,
        entities: List[Entity],
    ):
        raise NotImplementedError


class BasicMonster(AI):
    def __init__(self):
        super(BasicMonster, self).__init__()

    def take_turn(
        self,
        target: Entity,
        fov_map: tcod.map.Map,
        game_map: GameMap,
        entities: List[Entity],
    ):
        results = []

        monster = self.owner
        if fov_map.fov[monster.x, monster.y]:
            if monster.position.distance_to(target) >= 2:
                monster.move_astar(target=target, game_map=game_map, entities=entities)
            elif target.fighter.hp > 0:
                attack_results = monster.fighter.attack(target=target)
                results.extend(attack_results)

        return results


class ConfusedMonster(AI):
    def __init__(self, previous_ai: AI, number_of_turns: int = 10):
        self.previous_ai: AI = previous_ai
        self.number_of_turns: int = number_of_turns

    def take_turn(
        self,
        target: Entity,
        fov_map: tcod.map.Map,
        game_map: GameMap,
        entities: List[Entity]
    ):
        results = []

        if self.number_of_turns > 0:
            random_x = self.owner.x + random.randint(0, 2) - 1
            random_y = self.owner.y + random.randint(0, 2) - 1

            if random_x != self.owner.x and random_y != self.owner.y:
                self.owner.move_towards(target_position=Point(random_x, random_y), game_map=game_map, entities=entities)

            self.number_of_turns -= 1
        else:
            self.owner.ai = self.previous_ai
            results.append({"message": Message(f"The {self.owner.name} is no longer confused!", Colors.RED)})

        return results
