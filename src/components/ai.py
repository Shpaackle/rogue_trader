from __future__ import annotations

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    import tcod.map
    from entity import Entity
    from map_objects.game_map import GameMap


class BasicMonster:
    owner = None

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
