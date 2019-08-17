from __future__ import annotations

import json
import os
from typing import List, Optional, TYPE_CHECKING

from camera import Camera
from colors import Colors
from components import Fighter, Inventory, Level
from constants import CONSTANTS
from entity import Entity
from game_messages import MessageLog, Message
from game_states import GameStates
from map_objects import GameMap, MapGenerator, Point
from render_functions import RenderLayer

if TYPE_CHECKING:
    import tcod.map

    # from camera import Camera
    # from entity import Entity
    from map_objects import GameMap


class Game:
    def __init__(self):
        self.map_generator: Optional[MapGenerator] = None
        self.current_state: Optional[GameStates] = None
        self.previous_state: Optional[GameStates] = None
        self.player: Optional[Entity] = None
        self.entities: Optional[List[Entity]] = None
        self.message_log: Optional[MessageLog] = None
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
    def game_state(self) -> GameStates:
        return self.current_state

    @game_state.setter
    def game_state(self, new_state: GameStates):
        self.current_state = new_state

    def save_game(self):
        player_index = self.entities.index(self.player)
        entities_json_data = [entity.to_json() for entity in self.entities]
        game_map_json_data = self.game_map.to_json()
        message_log_json_data = self.message_log.to_json()
        game_state_json_data = self.game_state.value
        camera_json_data = self.camera.to_json()

        json_data = {
            "player_index": player_index,
            "entities": entities_json_data,
            "game_map": game_map_json_data,
            "message_log": message_log_json_data,
            "game_state": game_state_json_data,
            "camera": camera_json_data,
        }

        with open("save_game.json", "w") as save_file:
            json.dump(json_data, save_file, indent=4)

    @classmethod
    def load_game(cls):
        if not os.path.isfile("save_game.json"):
            raise FileNotFoundError

        with open("save_game.json") as save_file:
            json_data = json.load(save_file)

        entities = [
            Entity.from_json(json_data=entity_json_data)
            for entity_json_data in json_data["entities"]
        ]
        player = entities[json_data["player_index"]]

        game_map = GameMap.from_json(json_data=json_data["game_map"])
        message_log = MessageLog.from_json(json_data=json_data["message_log"])
        game_state = GameStates(json_data["game_state"])

        game = cls()
        game.map_generator: Optional[MapGenerator] = MapGenerator(
            map_width=CONSTANTS.map_width, map_height=CONSTANTS.map_height
        )
        game.entities = entities
        game.player = player

        game.map_generator.game_map = game_map
        game.message_log = message_log
        game.current_state = game_state

        game.camera: Camera = Camera.from_json(json_data=json_data, player=player)

        return game

    @classmethod
    def new_game(cls) -> Game:
        game = cls()
        game.map_generator: Optional[MapGenerator] = MapGenerator(
            map_width=CONSTANTS.map_width, map_height=CONSTANTS.map_height
        )
        game.current_state: Optional[GameStates] = GameStates.PLAYER_TURN
        game.previous_state: Optional[GameStates] = GameStates.PLAYER_TURN

        fighter_component: Fighter = Fighter(
            hp=CONSTANTS.player_hp,
            defense=CONSTANTS.player_defense,
            power=CONSTANTS.player_power,
        )
        inventory_component: Inventory = Inventory(capacity=26)
        level_component = Level()
        player: Optional[Entity] = Entity(
            position=Point(0, 0),
            char="@",
            color=Colors.WHITE,
            name="Player",
            blocks=True,
            render_order=RenderLayer.ACTOR,
            fighter=fighter_component,
            inventory=inventory_component,
            level=level_component
        )
        game.player: Optional[Entity] = player
        game.entities: Optional[List[Entity]] = [player]

        game.message_log: Optional[MessageLog] = MessageLog(
            x=CONSTANTS.message_x,
            width=CONSTANTS.message_width,
            height=CONSTANTS.message_height,
        )
        game.game_running: bool = True
        game.camera: Optional[Camera] = Camera(player=game.player)

        return game

    def next_floor(self):
        entities = [self.player]
        dungeon_level = self.map_generator.dungeon_level

        self.map_generator.generate_caves(width=CONSTANTS.map_width, height=CONSTANTS.map_height, entities=entities)

        self.game_map.dungeon_level = dungeon_level + 1

        self.map_generator.place_entities(
            entities=entities,
            min_monsters=CONSTANTS.min_monsters,
        )

        self.player.fighter.heal(self.player.fighter.max_hp // 2)
        self.player.position = self.map_generator.player_start_point

        self.message_log.add_message(Message("You take a moment to rest, and recover your strength.", Colors.LIGHT_VIOLET))

        self.entities = entities
        self.camera.recenter()
