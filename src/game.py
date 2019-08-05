from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from constants import CONSTANTS
from game_messages import MessageLog
from game_states import GameStates
from map_objects import MapGenerator

if TYPE_CHECKING:
    import tcod.map

    from camera import Camera
    from entity import Entity
    from map_objects import GameMap


class Game:
    def __init__(self):
        self.map_generator: MapGenerator = MapGenerator(map_width=CONSTANTS.map_width, map_height=CONSTANTS.map_height)
        self.current_state: GameStates = GameStates.PLAYER_TURN
        self.previous_state: GameStates = GameStates.PLAYER_TURN
        self.player: Entity = CONSTANTS.create_player()
        self.entities: List[Entity] = [self.player]
        self.message_log: MessageLog = MessageLog(x=CONSTANTS.message_x, width=CONSTANTS.message_width, height=CONSTANTS.message_height)
        self.fov_map: Optional[tcod.map.Map] = None
        self.game_running: bool = True
        self.camera: Optional[Camera] = None

    @property
    def game_map(self) -> GameMap:
        return self.map_generator.game_map

    def change_state(self, next_state: GameStates):
        self.previous_state = self.current_state
        self.current_state = next_state

    @property
    def game_state(self):
        return self.current_state

    @game_state.setter
    def game_state(self, value):
        self.current_state = value
