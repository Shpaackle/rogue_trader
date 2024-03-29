from __future__ import annotations

import random
from queue import Queue
from typing import List, Dict

import numpy as np

from colors import Colors
from components import BasicMonster, Equippable, Fighter, Item, Stairs
# from components.item import Item
from constants import CONSTANTS
from entity import Entity
from equipment_slots import EquipmentSlots
from game_messages import Message, MessageLog
from item_functions import cast_confuse, cast_fireball, cast_lightning, heal
from map_objects.point import Point
from map_objects.game_map import GameMap
from map_objects.tile import Tile
from random_utils import from_dungeon_level, random_choice_from_dict
from render_functions import RenderLayer


INITIAL_CHANCE = 0.4
FIRST_STEP_MIN = 5
FIRST_STEP_MAX = 2
FIRST_STEP_REPEATS = 4
SECOND_STEP_MIN = 5
SECOND_STEP_MAX = -1
SECOND_STEP_REPEATS = 2
MIN_CAVE_SIZE = 20


class MapGenerator:
    cave: List[Point]

    def __init__(self, map_width: int, map_height: int):
        self.game_map: GameMap = GameMap(width=map_width, height=map_height)
        self.visited_map: np.array = np.full_like(
            self.game_map.transparent, fill_value=False, order="F"
        )

    @property
    def player_start_point(self) -> Point:
        return random.choice(self.cave)

    @property
    def map_width(self):
        return self.game_map.width

    @property
    def map_height(self):
        return self.game_map.height

    def make_map(
        self,
        width: int,
        height: int,
        entities: List[Entity],
        min_monsters: int,
    ):
        self.generate_caves(width=width, height=height, entities=entities)

        self.place_entities(
            entities=entities,
            min_monsters=min_monsters,
        )

    def generate_caves(self, width: int, height: int, entities: List[Entity]):
        self.initialize_cave(width=width, height=height)
        for _ in range(FIRST_STEP_REPEATS):
            self.cave_smooth_step(min_count=FIRST_STEP_MIN, max_count=FIRST_STEP_MAX)
        for _ in range(SECOND_STEP_REPEATS):
            self.cave_smooth_step(min_count=SECOND_STEP_MIN, max_count=SECOND_STEP_MAX)

        caves: List[List[Point]] = self.find_caves()

        cave: List[Point] = self.isolate_main_cave(caves)
        self.cave = self.remove_small_walls(cave)

        stairs_component = Stairs(self.dungeon_level + 1)
        point: Point = random.choice(self.cave)
        down_stairs: Entity = Entity(position=point, char=">", color=Colors.WHITE, name="Stairs", render_order=RenderLayer.STAIRS, stairs=stairs_component)
        entities.append(down_stairs)

    @property
    def dungeon_level(self):
        return self.game_map.dungeon_level

    @dungeon_level.setter
    def dungeon_level(self, value: int):
        self.game_map.dungeon_level = value

    def find_caves(self) -> List[List[Point]]:
        caves: List[List[Point]] = list()
        self.visited_map[:] = False

        for i in range(1, self.map_height - 1):
            for j in range(1, self.map_width - 1):
                point = Point(x=j, y=i)
                wall = self.game_map.is_blocked(point)
                visited = self.visited_map[j, i]
                if visited or wall:
                    continue

                current_cave = self.explore_cave(start_point=point)
                caves.append(current_cave)

        return caves

    def explore_cave(self, start_point: Point) -> List[Point]:
        cave: List[Point] = [start_point]

        unexplored = Queue()
        unexplored.put(start_point)
        self.visited_map[start_point.x, start_point.y] = True

        while not unexplored.empty():
            current: Point = unexplored.get()
            for neighbor in current.all_neighbors:
                visited = self.visited_map[neighbor.x, neighbor.y]
                blocked = self.game_map.is_blocked(point=neighbor)
                if not visited and not blocked:
                    unexplored.put(neighbor)
                    cave.append(neighbor)
                    self.visited_map[neighbor.x, neighbor.y] = True

        return cave

    def cave_smooth_step(self, min_count: int, max_count: int):
        for i in range(1, self.map_height - 1):
            for j in range(1, self.map_width - 1):
                point = Point(x=j, y=i)
                count1 = self.game_map.count_one_step_neighbors(center=point)
                count2 = self.game_map.count_two_step_neighbors(center=point)

                if count1 >= min_count:
                    self.game_map.place_tile(point=point, tile=Tile.cave(point=point))
                elif count2 <= max_count:
                    self.game_map.place_tile(point=point, tile=Tile.cave(point=point))
                else:
                    self.game_map.place_tile(point=point, tile=Tile.floor(point=point))

    def initialize_cave(self, width: int, height: int):
        game_map = GameMap(width=width, height=height)
        game_map.walkable[:] = True
        game_map.transparent[:] = True

        for i in range(height):
            for j in range(width):
                point = Point(x=j, y=i)
                if i == 0 or j == 0 or i == height - 1 or j == width - 1:
                    game_map.place_tile(point, Tile.cave(point=point))

                if random.random() < INITIAL_CHANCE:
                    game_map.place_tile(point, Tile.cave(point=point))

        self.game_map = game_map

    def isolate_main_cave(self, caves: List[List[Point]]) -> List[Point]:
        if len(caves) == 1:
            return caves[0]

        cave_sort: List[List[Point]] = sorted(caves, key=len, reverse=True)
        largest = cave_sort[0]
        for cave in cave_sort[1:]:
            for point in cave:
                self.game_map.place_tile(point, tile=Tile.cave(point=point))
        return largest

    def remove_small_walls(self, cave: List[Point]) -> List[Point]:
        for i in range(1, self.map_height - 1):
            for j in range(1, self.map_width - 1):
                point = Point(x=j, y=i)
                wall = self.game_map.is_blocked(point)
                if not wall:
                    continue
                if self.game_map.count_one_step_neighbors(point) == 1:
                    cave.append(point)
                    self.game_map.place_tile(point=point, tile=Tile.floor(point=point))
        return cave

    def find_tile(self, point: Point) -> Tile:
        label = self.game_map.cave_map[point.x, point.y]
        if label == "CAVE":
            tile = Tile.cave(point)
        elif label == "FLOOR":
            tile = Tile.floor(point)
        else:
            tile = Tile.empty(point)
        return tile

    def place_entities(
        self,
        entities: List[Entity],
        min_monsters: int,
    ):
        max_monsters: int = from_dungeon_level(table=[[10, 1], [14, 4], [18, 6]], dungeon_level=self.dungeon_level)
        max_items: int = from_dungeon_level(table=[[8, 1], [16, 4]], dungeon_level=self.dungeon_level)

        number_of_monsters: int = random.randint(min_monsters, max_monsters)
        number_of_items: int = random.randint(1, max_items)

        monster_chances: Dict[str, int] = {
            "orc": 80,
            "troll": from_dungeon_level(table=[[15, 3], [30, 5], [60, 7]], dungeon_level=self.dungeon_level)
        }

        item_chances: Dict[str, int] = {
            "healing_potion": 35,
            "sword": from_dungeon_level(table=[[5, 4]], dungeon_level=self.dungeon_level),
            "shield": from_dungeon_level(table=[[15, 8]], dungeon_level=self.dungeon_level),
            "lightning_scroll": from_dungeon_level(table=[[25, 4]], dungeon_level=self.dungeon_level),
            "fireball_scroll": from_dungeon_level(table=[[25, 6]], dungeon_level=self.dungeon_level),
            "confusion_scroll": from_dungeon_level(table=[[10, 2]], dungeon_level=self.dungeon_level)
        }

        for i in range(number_of_monsters):
            point: Point = random.choice(self.cave)

            if not any([entity for entity in entities if entity.position == point]):
                monster_choice = random_choice_from_dict(monster_chances)
                if monster_choice == "orc":
                    fighter_component: Fighter = Fighter(hp=20, defense=0, power=4, xp=35)
                    ai_component: BasicMonster = BasicMonster()
                    monster: Entity = Entity(
                        position=point,
                        char="o",
                        color=Colors.LIGHT_GREEN,
                        name="Orc",
                        blocks=True,
                        render_order=RenderLayer.ACTOR,
                        fighter=fighter_component,
                        ai=ai_component,
                    )
                else:
                    fighter_component: Fighter = Fighter(hp=30, defense=2, power=8, xp=100)
                    ai_component: BasicMonster = BasicMonster()
                    monster: Entity = Entity(
                        position=point,
                        char="T",
                        color=Colors.DARKER_GREEN,
                        name="Troll",
                        blocks=True,
                        render_order=RenderLayer.ACTOR,
                        fighter=fighter_component,
                        ai=ai_component,
                    )

                entities.append(monster)

        for i in range(number_of_items):
            point: Point = random.choice(self.cave)

            if not any([entity for entity in entities if entity.position == point]):
                item_choice: str = random_choice_from_dict(item_chances)

                if item_choice == "healing_potion":
                    item_component: Item = Item(use_function=heal, amount=40)
                    item: Entity = Entity(
                        position=point,
                        char="!",
                        color=Colors.VIOLET,
                        name="Healing Potion",
                        render_order=RenderLayer.ITEM,
                        item=item_component,
                    )
                elif item_choice == "sword":
                    equippable_component = Equippable(slot=EquipmentSlots.MAIN_HAND, power_bonus=3)
                    item = Entity(
                        position=point,
                        char="/",
                        color=Colors.SKY,
                        name="Sword",
                        equippable=equippable_component
                    )
                elif item_choice == "shield":
                    equippable_component = Equippable(slot=EquipmentSlots.OFF_HAND, defense_bonus=1)
                    item = Entity(
                        position=point,
                        char="[",
                        color=Colors.DARKER_ORANGE,
                        name="Shield",
                        equippable=equippable_component
                    )
                elif item_choice == "fireball_scroll":
                    item_component: Item = Item(
                        use_function=cast_fireball,
                        targeting=True,
                        targeting_message=Message(
                            "Left-click a target tile for the fireball, or right-click to cancel.",
                            Colors.LIGHT_CYAN,
                        ),
                        damage=25,
                        radius=3,
                    )
                    item = Entity(
                        position=point,
                        char="#",
                        color=Colors.RED,
                        name="Fireball Scroll",
                        render_order=RenderLayer.ITEM,
                        item=item_component,
                    )
                elif item_choice == "confusion_scroll":
                    item_component: Item = Item(
                        use_function=cast_confuse,
                        targeting=True,
                        targeting_message=Message(
                            "Left-click an enemy to confuse it, or right-click to cancel.",
                            Colors.LIGHT_CYAN,
                        ),
                    )
                    item: Entity = Entity(
                        position=point,
                        char="#",
                        color=Colors.LIGHT_PINK,
                        name="Confusion Scroll",
                        render_order=RenderLayer.ITEM,
                        item=item_component,
                    )
                else:
                    item_component: Item = Item(
                        use_function=cast_lightning, damage=40, maximum_range=5
                    )
                    item: Entity = Entity(
                        position=point,
                        char="#",
                        color=Colors.YELLOW,
                        name="Lightning Scroll",
                        render_order=RenderLayer.ITEM,
                        item=item_component,
                    )

                entities.append(item)
