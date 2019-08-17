from __future__ import annotations

import random
from typing import Iterable


def from_dungeon_level(table, dungeon_level: int):
    for (value, level) in reversed(table):
        if dungeon_level >= level:
            return value

    return 0


def random_choice_index(chances: Iterable):
    random_chance = random.randint(1, sum(chances))

    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w

        if random_chance <= running_sum:
            return choice
        choice += 1


def random_choice_from_dict(choice_dict: dict):
    choices = list(choice_dict.keys())
    chances = list(choice_dict.values())
    # choices, chances = choice_dict.items()

    return choices[random_choice_index(chances)]
