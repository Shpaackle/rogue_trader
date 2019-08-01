from __future__ import annotations

import random
from queue import Queue
from typing import List

import numpy as np

from colors import Colors
from components.ai import BasicMonster
from components.fighter import Fighter
from entity import Entity
from map_objects.point import Point
from map_objects.game_map import GameMap
from map_objects.tile import Tile
from render_functions import RenderOrder


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
        max_monsters: int,
    ):
        self.generate_caves(width=width, height=height)

        self.place_entities(
            entities=entities, min_monsters=min_monsters, max_monsters=max_monsters
        )

    def generate_caves(self, width: int, height: int):
        self.initialize_cave(width=width, height=height)
        for _ in range(FIRST_STEP_REPEATS):
            self.cave_smooth_step(min_count=FIRST_STEP_MIN, max_count=FIRST_STEP_MAX)
        for _ in range(SECOND_STEP_REPEATS):
            self.cave_smooth_step(min_count=SECOND_STEP_MIN, max_count=SECOND_STEP_MAX)

        caves: List[List[Point]] = self.find_caves()

        cave: List[Point] = self.isolate_main_cave(caves)
        self.cave = self.remove_small_walls(cave)
        print("finished caves")

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
                    self.game_map.place_tile(point=point, tile=Tile.empty(point=point))
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
        self, entities: List[Entity], min_monsters: int, max_monsters: int
    ):
        number_of_monsters: int = random.randint(min_monsters, max_monsters)

        for i in range(number_of_monsters):
            point: Point = random.choice(self.cave)

            if not any([entity for entity in entities if entity.position == point]):
                if random.randint(0, 100) < 80:
                    fighter_component: Fighter = Fighter(hp=10, defense=0, power=3)
                    ai_component: BasicMonster = BasicMonster()
                    monster: Entity = Entity(
                        position=point,
                        char="o",
                        color=Colors.LIGHT_GREEN,
                        name="Orc",
                        blocks=True,
                        render_order=RenderOrder.ACTOR,
                        fighter=fighter_component,
                        ai=ai_component,
                    )
                else:
                    fighter_component: Fighter = Fighter(hp=16, defense=1, power=4)
                    ai_component: BasicMonster = BasicMonster()
                    monster: Entity = Entity(
                        position=point,
                        char="T",
                        color=Colors.DARKER_GREEN,
                        name="Troll",
                        blocks=True,
                        render_order=RenderOrder.ACTOR,
                        fighter=fighter_component,
                        ai=ai_component,
                    )

                entities.append(monster)
