import random

import numpy as np
import tcod
from bearlibterminal import terminal as blt
from tcod.map import Map

from entity import Entity
from map_objects.point import Point
from rect import Rect


FILLED = 1
EMPTY = 0


class GameMap(Map):
    def __init__(self, width: int, height: int):
        super(GameMap, self).__init__(width=width, height=height, order="F")

        # self.transparent[:] = False
        # self.walkable[:] = False
        # self.cave_map = np.zeros_like(self.walkable, dtype=int, order="F")
        self.cave_map: np.array = np.zeros((width, height), order="F")

    def is_blocked(self, point: Point) -> bool:
        if not self.walkable[point.x, point.y]:
            return True

        return False

    def create_room(self, room: Rect):
        for x in range(room.x + 1, room.right):
            for y in range(room.y + 1, room.bottom):
                self.walkable[x, y] = True
                self.transparent[x, y] = True

    # def make_cave(
    #     self,
    #     map_width: int,
    #     map_height: int,
    #     player: Entity,
    #     initial_chance: float = 0.4,
    # ):
    #     self.initialize_cave(map_width, map_height, initial_chance)
    #     for i in range(1, map_height - 1):
    #         for j in range(1, map_width - 1):
    #             count1 = self.one_step_neighbor_count(
    #                 Point(x=j, y=i)
    #             )  # 1-step neighbors
    #             count2 = self.two_step_neighbor_count(
    #                 Point(x=j, y=i)
    #             )  # 2-step neighbors

    def create_h_tunnel(self, x1: int, x2: int, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.walkable[x, y] = True
            self.transparent[x, y] = True

    def create_v_tunnel(self, x: int, y1: int, y2: int):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.walkable[x, y] = True
            self.transparent[x, y] = True

    # def make_map(
    #     self,
    #     max_rooms: int,
    #     room_min_size: int,
    #     room_max_size: int,
    #     map_width: int,
    #     map_height: int,
    #     player: Entity,
    #     num_attempts: int = 200,
    # ):
    #     rooms = []
    #     num_rooms = 0

    # def initialize_cave(self, map_width: int, map_height: int, initial_chance: float):
    #     buffer_map = np.copy(self.cave_map)
    #
    #     for i in range(map_height):
    #         for j in range(map_width):
    #             if i == 0 or j == 0 or i == map_height - 1 or j == map_width - 1:
    #                 buffer_map[j, i] = FILLED
    #                 continue
    #
    #             if random.random() < initial_chance:
    #                 buffer_map[j, i] = FILLED
    #             else:
    #                 buffer_map[j, i] = EMPTY
    #
    #     self.cave_map = buffer_map
    #
    #     for i in range(self.height):
    #         for j in range(self.width):
    #             if self.cave_map[j, i] == FILLED:
    #                 self.walkable[j, i] = False
    #                 self.transparent[j, i] = False
    #             else:
    #                 self.walkable[j, i] = True
    #                 self.transparent[j, i] = True

    # def one_step_neighbor_count(self, point: Point) -> int:
    #     count = 0
    #     for neighbor in point.all_neighbors:
    #         if (
    #             neighbor.x < 0
    #             or self.width <= neighbor.x
    #             or neighbor.y < 0
    #             or self.height <= neighbor.y
    #         ):
    #             pass
    #         elif self.cave_map[neighbor.x, neighbor.y] == FILLED:
    #             count += 1
    #     return count

    def in_bounds(self, point: Point) -> bool:
        return 0 <= point.x < self.width and 0 <= point.y < self.height

    def count_one_step_neighbors(self, center: Point) -> int:
        # TODO: refactor to make more generic
        # combine with two_step to take a steps parameter and returns multiple values
        count = 0
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                point = Point(x=center.x + j, y=center.y + i)
                if not self.in_bounds(point=point):
                    continue
                if self.cave_map[point.x, point.y]:
                    count += 1

        return count

    # TODO: refactor to make more generic
    def count_two_step_neighbors(self, center: Point) -> int:
        count = 0
        for i in range(-2, 2):
            for j in range(-2, 2):
                if abs(i) == 2 and abs(j) == 2:
                    continue

                point = Point(x=center.x + j, y=center.y + i)
                if not self.in_bounds(point):
                    continue
                if self.cave_map[point.x, point.y]:
                    count += 1

        return count

    # def two_step_neighbor_count(self, point: Point) -> int:
    #     count = 0
    #     for i in range(-2, 2):
    #         for j in range(-2, 2):
    #             if (abs(i) == 2 and abs(j) == 2):
    #                 continue
    #
    #             neighbor = point + Point(x=j, y=i)
    #             if (
    #                 neighbor.x < 0
    #                 or self.width <= neighbor.x
    #                 or neighbor.y < 0
    #                 or self.height <= neighbor.y
    #             ):
    #                 pass
    #             elif self.cave_map[neighbor.x, neighbor.y] == FILLED:
    #                 count += 1
    #     return count

    # def cave_smooth_step(self, min_count: int, max_count: int):
    #
    #     for i in range(1, self.height - 1):
    #         for j in range(1, self.width - 1):
    #             point = Point(x=j, y=i)
    #             count1 = self.one_step_neighbor_count(point)
    #             count2 = self.two_step_neighbor_count(point)
    #             if count1 >= min_count or count2 < max_count:
    #                 self.cave_map[j, i] = FILLED
    #             else:
    #                 self.cave_map[j, i] = EMPTY

    def place_tile(self, point: Point, tile: str):
        if tile == "CAVE":
            self.walkable[point.x, point.y] = False
            self.transparent[point.x, point.y] = False
            self.cave_map[point.x, point.y] = FILLED
        elif tile == "EMPTY":
            self.walkable[point.x, point.y] = True
            self.transparent[point.x, point.y] = True
            self.cave_map[point.x, point.y] = EMPTY

    def render(self, colors):
        for y in range(self.height):
            for x in range(self.width):
                # wall = self.is_blocked(x, y)
                wall = self.cave_map[x, y] == FILLED

                if wall:
                    blt.printf(
                        x=x, y=y, s=f"[color={colors.get('dark_wall')}]#[/color]"
                    )
                else:
                    blt.printf(
                        x=x, y=y, s=f"[color={colors.get('dark_ground')}].[/color]"
                    )
