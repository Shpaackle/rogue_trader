from enum import auto, Enum


class GameStates(Enum):
    PLAYER_TURN = auto()
    ENEMY_TURN = auto()
    PLAYER_DEAD = auto()
    SHOW_INVENTORY = auto()
    DROP_INVENTORY = auto()
    TARGETING = auto()
    MAIN_MENU = auto()
    LEVEL_UP = auto()
    CHARACTER_SCREEN = auto()
