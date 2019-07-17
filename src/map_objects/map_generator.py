import random
from queue import Queue
from typing import List

import numpy as np

from map_objects.point import Point
from map_objects.game_map import GameMap


INITIAL_CHANCE = 0.4
FIRST_STEP_MIN = 5
FIRST_STEP_MAX = 2
FIRST_STEP_REPEATS = 4
SECOND_STEP_MIN = 5
SECOND_STEP_MAX = -1
SECOND_STEP_REPEATS = 2


class MapGenerator:
    game_map: GameMap
    unconnected_caves: List[List[Point]]
    visited_map: np.array

    @property
    def map_width(self):
        return self.game_map.width

    @property
    def map_height(self):
        return self.game_map.height

    def create_new_map(self):
        # initialize map
        ...

    def generate_caves(self, width: int, height: int):
        self.initialize_cave(width=width, height=height)
        for _ in range(FIRST_STEP_REPEATS):
            self.cave_smooth_step(min_count=FIRST_STEP_MIN, max_count=FIRST_STEP_MAX)
        for _ in range(SECOND_STEP_REPEATS):
            self.cave_smooth_step(min_count=SECOND_STEP_MIN, max_count=SECOND_STEP_MAX)

        self.unconnected_caves: List[List[Point]] = self.find_caves()
        print("finished caves")

    def find_caves(self) -> List[List[Point]]:
        caves: List[List[Point]] = list()
        self.visited_map: np.array = np.full_like(self.game_map.transparent, False, order="F")

        for i in range(1, self.map_height - 1):
            for j in range(1, self.map_width - 1):
                point = Point(x=j, y=i)
                wall = self.game_map.is_blocked(point)
                visited = self.visited_map[j, i]
                if visited or wall:
                    continue

                current_cave = self.fill_cave(start_point=point)
                caves.append(current_cave)

        return caves

    def fill_cave(self, start_point: Point) -> List[Point]:
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

    """
        for i in range(1, self.height - 1):
            for j in range(1, self.width - 1):
                point = Point(x=j, y=i)
                count1 = self.find_one_step_neighbors(center=point)
                count2 = self.find_two_step_neighbors(center=point)

                if count1 >= min_count:
                    self.cave_map[point.x, point.y] = FILLED
                elif count2 <= max_count:
                    self.cave_map[point.x, point.y] = FILLED
                else:
                    self.cave_map[point.x, point.y] = EMPTY
    """
    def cave_smooth_step(self, min_count: int, max_count: int):
        for i in range(1, self.map_height - 1):
            for j in range(1, self.map_width - 1):
                point = Point(x=j, y=i)
                count1 = self.game_map.count_one_step_neighbors(center=point)
                count2 = self.game_map.count_two_step_neighbors(center=point)

                if count1 >= min_count:
                    # set map @ point to FILLED
                    self.game_map.place_tile(point=point, tile="CAVE")
                elif count2 <= max_count:
                    # set map @ point to FILLED
                    self.game_map.place_tile(point=point, tile="CAVE")
                else:
                    # set map @ point to EMPTY
                    self.game_map.place_tile(point=point, tile="EMPTY")

    def initialize_cave(self, width: int, height: int):
        game_map = GameMap(width=width, height=height)
        game_map.walkable[:] = True
        game_map.transparent[:] = True

        for i in range(height):
            for j in range(width):
                point = Point(x=j, y=i)
                if i == 0 or j == 0 or i == height - 1 or j == width - 1:
                    game_map.place_tile(point, "CAVE")

                if random.random() < INITIAL_CHANCE:
                    game_map.place_tile(point, "CAVE")

        self.game_map = game_map
