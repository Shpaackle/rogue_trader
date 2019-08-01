from __future__ import annotations

from typing import List, Optional

from bearlibterminal import terminal as blt
import tcod

from colors import Colors
from map_objects.game_map import GameMap
from map_objects.point import Point
from render_functions import RenderOrder


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    def __init__(
        self,
        position: Point,
        char: str,
        color: Colors,
        name: str,
        blocks: bool = False,
        render_order: RenderOrder = RenderOrder.CORPSE,
        fighter=None,
        ai=None,
    ):
        self.position: Point = position
        self.char: str = char
        self.color: Colors = color
        self.name: str = name
        self.blocks: bool = blocks
        self.render_order: RenderOrder = render_order
        self.fighter = fighter
        self.ai = ai

        if self.fighter:
            self.fighter.owner = self

        if self.ai:
            self.ai.owner = self

    @property
    def x(self) -> int:
        return self.position.x

    @x.setter
    def x(self, value: int):
        self.position = Point(value, self.y)

    @property
    def y(self) -> int:
        return self.position.y

    @y.setter
    def y(self, value):
        self.position = Point(self.x, value)

    def move(self, point: Point):
        """ Move the entity in a particular direction """
        self.position += point

    def move_towards(
        self, target_position: Point, game_map: GameMap, entities: List["Entity"]
    ):
        d: Point = target_position - self.position
        distance = self.position.distance_to(target_position)

        movement = Point(x=int(round(d.x / distance)), y=int(round(d.y / distance)))

        if not (
            game_map.is_blocked(target_position + movement)
            or get_blocking_entities_at_location(entities, self.position + movement)
        ):
            self.move(movement)

    def move_astar(self, target: "Entity", entities: List["Entity"], game_map: GameMap):
        # Create a FOV map that has the dimensions of the map
        fov: tcod.map.Map = tcod.map.Map(
            width=game_map.width, height=game_map.height, order="F"
        )

        # Scan the current map each turn and set all the walls as unwalkable
        for tile in game_map.tiles:
            fov.transparent[tile.x, tile.y] = not tile.blocks_sight
            fov.walkable[tile.x, tile.y] = not tile.blocked

        # Scan all the objects to see if there are objects that must be navigated around
        # Check also that the object isn't self or the target (so that the start and the end points are free)
        # The AI class handles the situation is self is next to the target so it will not use this A* function anyway
        for entity in entities:
            if entity.blocks and entity != self and entity != target:
                # Set the tile as a wall so it must be navigated around
                fov.transparent[entity.x, entity.y] = True
                fov.walkable[entity.x, entity.y] = False

        # Allocate an A* path
        # The 1.41 is the normal diagonal cost of moving, it can be set as 0.0 if diagonal moves are prohibited
        my_path = tcod.path_new_using_map(fov, 1.41)

        # Compute the path between self's coordinates and the target's coordinates
        tcod.path_compute(my_path, self.x, self.y, target.x, target.y)

        # Check if the path exists, and in this case, also the path is shorter than 25 tiles
        # The path size matters if you want the monster to use alternative longer paths (for
        # example through other rooms) if for example the player is in a corridor
        # It makes sense to keep the path size relatively low to keep monsters from running around
        # the map if there's an alternative path really far away
        if not tcod.path_is_empty(my_path) and tcod.path_size(my_path) < 25:
            # Find the next coordinates in the computed full path
            x, y = tcod.path_walk(my_path, True)
            if x or y:
                # Set self's coordinates to the next path tile
                self.x = x
                self.y = y
        else:
            # Keep the old move function as a backup so that is there are no paths (for example
            # another monster blocks a corridor it will still try to move towards the player
            # (closer to the corridor opening)
            self.move_towards(
                target_position=target.position, game_map=game_map, entities=entities
            )

        # Delete the path to free memory
        tcod.path_delete(my_path)

    def draw(self, point: Point = None):
        """ Draw the entity to the terminal """
        if point is None:
            point = self.position
        color = blt.color_from_argb(*self.color.argb)
        blt.printf(
            x=point.x * 2, y=point.y * 2, s=f"[font=map][color={color}]{self.char}[/color][/font]"
        )


def get_blocking_entities_at_location(
    entities: List[Entity], destination: Point
) -> Optional[Entity]:
    for entity in entities:
        if entity.blocks and entity.position == destination:
            return entity

    return None
