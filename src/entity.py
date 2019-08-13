from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from bearlibterminal import terminal as blt
import tcod

from colors import Colors
import components
from map_objects.game_map import GameMap
from map_objects.point import Point
from render_functions import RenderLayer

if TYPE_CHECKING:
    from components.entity_component import EntityComponent
    import tcod.map


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
        render_order: RenderLayer = RenderLayer.CORPSE,
        fighter: Optional[components.Fighter] = None,
        ai: Optional[EntityComponent] = None,
        item: Optional[components.Item] = None,
        inventory: Optional[components.Inventory] = None,
        stairs: Optional[components.Stairs] = None,
        level: Optional[components.Level] = None
    ):
        self.position: Point = position
        self.char: str = char
        self.color: Colors = color
        self.name: str = name
        self.blocks: bool = blocks
        self.render_order: RenderLayer = render_order
        self.fighter: Optional[components.Fighter] = fighter
        self.ai: Optional[EntityComponent] = ai
        self.item: Optional[components.Item] = item
        self.inventory: Optional[components.Inventory] = inventory
        self.stairs: Optional[components.Stairs] = stairs
        self.level: Optional[components.Level] = level

        if self.fighter:
            self.fighter.owner = self

        if self.ai:
            self.ai.owner = self

        if self.item:
            self.item.owner = self

        if self.inventory:
            self.inventory.owner = self

        if self.stairs:
            self.stairs.owner = self

        if self.level:
            self.level.owner = self

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
        distance: float = self.distance_to(target_position)

        x: int = int(round(d.x / distance))
        y: int = int(round(d.y / distance))
        movement: Point = Point(x=x, y=y)

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
        blt.layer(self.render_order.value)
        blt.printf(
            x=point.x * 2,
            y=point.y * 2,
            s=f"[font=map][color={color}]{self.char}[/color][/font]",
        )

    def to_json(self) -> dict:
        json_data = {
            "x": self.position.x,
            "y": self.position.y,
            "char": self.char,
            "color": self.color.name,
            "name": self.name,
            "blocks": self.blocks,
            "render_order": self.render_order.value,
        }

        if self.ai:
            json_data["ai"] = self.ai.to_json()

        if self.fighter:
            json_data["fighter"] = self.fighter.to_json()

        if self.inventory:
            json_data["inventory"] = self.inventory.to_json()

        if self.item:
            json_data["item"] = self.item.to_json()

        if self.stairs:
            json_data["stairs"] = self.stairs.to_json()

        if self.level:
            json_data["level"] = self.level.to_json()

        return json_data

    @classmethod
    def from_json(cls, json_data):
        x: int = json_data.get("x")
        y: int = json_data.get("y")
        char: str = json_data.get("char")
        color: str = json_data.get("color")
        name: str = json_data.get("name")
        blocks: bool = json_data.get("blocks")
        render_order: RenderLayer = json_data.get("render_order")

        fighter_json: dict = json_data.get("fighter")
        ai_json: dict = json_data.get("ai")
        item_json: dict = json_data.get("item")
        inventory_json: dict = json_data.get("inventory")
        stairs_json: int = json_data.get("stairs")
        level_json: dict = json_data.get("level")

        if fighter_json:
            fighter = components.Fighter.from_json(json_data=fighter_json)
        else:
            fighter = None

        if item_json:
            item = components.Item.from_json(json_data=item_json)
        else:
            item = None

        if inventory_json:
            inventory = components.Inventory.from_json(json_data)
        else:
            inventory = None

        if stairs_json:
            stairs = components.Stairs(stairs_json)
        else:
            stairs = None

        if level_json:
            level = components.Level(current_level=level_json["current_level"], current_xp=level_json["current_xp"], level_up_base=level_json["level_up_base"], level_up_factor=level_json["level_up_factor"])
        else:
            level = None

        entity = Entity(
            position=Point(x=x, y=y),
            char=char,
            color=Colors[color],
            name=name,
            blocks=blocks,
            render_order=RenderLayer(render_order),
            fighter=fighter,
            item=item,
            inventory=inventory,
            stairs=stairs,
            level=level
        )

        if ai_json:
            ai_name: str = ai_json.get("name")

            if ai_name == components.BasicMonster.__name__:
                ai = components.BasicMonster.from_json(json_data=ai_json, owner=entity)
            elif ai_name == components.ConfusedMonster.__name__:
                ai = components.ConfusedMonster.from_json(json_data=ai_json, owner=entity)
            else:
                ai = None

            entity.ai = ai

        return entity

    def distance_to(self, point: Point) -> float:
        distance: float = self.position.distance_to(point)
        return distance


def get_blocking_entities_at_location(
    entities: List[Entity], destination: Point
) -> Optional[Entity]:
    for entity in entities:
        if entity.blocks and entity.position == destination:
            return entity

    return None
