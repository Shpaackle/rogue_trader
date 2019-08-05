from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from bearlibterminal import terminal as blt

from camera import Camera
from colors import Colors
from components.fighter import Fighter
from components.inventory import Inventory
from constants import CONSTANTS
from death_functions import kill_monster, kill_player
from entity import Entity, get_blocking_entities_at_location
from fov_functions import initialize_fov, recompute_fov
from game import Game
from game_messages import Message, MessageLog
from game_states import GameStates
from input_handlers import handle_keys, handle_mouse
from loader_functions.initialize_new_game import get_constants
from map_objects.game_map import GameMap
from map_objects.map_generator import MapGenerator
from map_objects import Point
from rect import Rect
from render_functions import render_all, RenderOrder

if TYPE_CHECKING:
    import tcod.map


def main():
    game = Game()
    game.map_generator.make_map(
        width=CONSTANTS.map_width,
        height=CONSTANTS.map_width,
        entities=game.entities,
        min_monsters=CONSTANTS.min_monsters,
        max_monsters=CONSTANTS.max_monsters,
        max_items=CONSTANTS.max_items
    )
    # map_generator.generate_caves(width=map_width, height=map_height)

    # game_map: GameMap = map_generator.game_map

    # fov_update: bool = True

    game.fov_map: tcod.map.Map = initialize_fov(game.game_map)

    # message_log: MessageLog = MessageLog(constants["message_x"], constants["message_width"], constants["message_height"])

    game.player.position: Point = game.map_generator.player_start_point

    game.camera: Camera = Camera(player=game.player, width=CONSTANTS.camera_width, height=CONSTANTS.camera_height)
    blt.open()
    blt.composition(True)
    blt.set(f"window: size={CONSTANTS.screen_width}x{CONSTANTS.screen_height}, title={CONSTANTS.window_title}, cellsize=8x8")
    blt.set("input: filter={keyboard, mouse+}")
    blt.set(f"{CONSTANTS.map_font}")
    blt.set(f"{CONSTANTS.ui_font}")
    blt.set(f"{CONSTANTS.bar_font}")
    blt.set(f"{CONSTANTS.hover_font}")

    game.game_state: GameStates = GameStates.PLAYER_TURN
    game.previous_game_state: GameStates = game.game_state

    targeting_item: Optional[Entity] = None

    mouse_position: Point = Point(x=blt.state(blt.TK_MOUSE_X)//2, y=blt.state(blt.TK_MOUSE_Y)//2)

    while game.game_running:
        if game.camera.fov_update:
            recompute_fov(
                game.fov_map, game.player.position, CONSTANTS.fov_radius, CONSTANTS.fov_light_walls, CONSTANTS.fov_algorithm
            )
        render_all(
            entities=game.entities,
            player=game.player,
            game_map=game.game_map,
            fov_map=game.fov_map,
            camera=game.camera,
            message_log=game.message_log,
            ui_panel=CONSTANTS.ui_panel,
            bar_width=CONSTANTS.bar_width,
            mouse_position=mouse_position,
            game_state=game.game_state
        )

        game.camera.fov_update = False

        # blt.refresh()

        if blt.has_input():
            terminal_input: int = blt.read()

            mouse_position = Point(x=blt.state(blt.TK_MOUSE_X) // 2, y=blt.state(blt.TK_MOUSE_Y) // 2)
            game.camera.fov_update = True

            action: dict = handle_keys(terminal_input, game.game_state)
            mouse_action: dict = handle_mouse(terminal_input, mouse_position)

            movement: Optional[Point] = action.get("move", None)
            pickup: bool = action.get("pickup", False)
            show_inventory: bool = action.get("show_inventory", False)
            drop_inventory: bool = action.get("drop_inventory", False)
            inventory_index: Optional[int] = action.get("inventory_index", None)
            exit_action: bool = action.get("exit", False)

            left_click = mouse_action.get("left_click")
            right_click = mouse_action.get("right_click")

            player_turn_results = []

            if show_inventory:
                game.change_state(GameStates.SHOW_INVENTORY)

            if drop_inventory:
                game.change_state(GameStates.DROP_INVENTORY)

            if inventory_index is not None and game.previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(game.player.inventory.items):
                item = game.player.inventory.items[inventory_index]

                if game.game_state == GameStates.SHOW_INVENTORY:
                    player_turn_results.extend(game.player.inventory.use(item, entities=game.entities, fov_map=game.fov_map))
                elif game.game_state == GameStates.DROP_INVENTORY:
                    player_turn_results.extend(game.player.inventory.drop_item(item))

            if game.game_state == GameStates.TARGETING:
                if left_click:
                    target_position: Point = game.camera.map_point(left_click)

                    item_use_results = game.player.inventory.use(targeting_item, entities=game.entities, fov_map=game.fov_map, target_position=target_position)
                    player_turn_results.extend(item_use_results)
                elif right_click:
                    player_turn_results.append({"targeting_cancelled": True})

            if exit_action:
                if game.game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
                    game.game_state = GameStates.PLAYER_TURN
                elif game.game_state == GameStates.TARGETING:
                    player_turn_results.append({"targeting_cancelled": True})

                else:
                    game.game_running = False

            # player_turn_results = []

            if movement and game.game_state == GameStates.PLAYER_TURN:
                destination = game.player.position + movement
                if not game.game_map.is_blocked(destination):
                    target = get_blocking_entities_at_location(
                        entities=game.entities, destination=destination
                    )

                    if target:
                        attack_results = game.player.fighter.attack(target=target)
                        player_turn_results.extend(attack_results)
                        game.camera.fov_update = True
                    else:
                        game.player.move(movement)
                        game.camera.recenter()

                        # fov_update = True

                    game.change_state(GameStates.ENEMY_TURN)
            elif pickup and game.game_state == GameStates.PLAYER_TURN:
                for entity in game.entities:
                    if entity.item and entity.position == game.player.position:
                        pickup_results = game.player.inventory.add_item(entity)
                        player_turn_results.extend(pickup_results)

                        break
                else:
                    game.message_log.add_message(Message("There is nothing here to pick up."))

            for player_turn_result in player_turn_results:
                message: Optional[Message] = player_turn_result.get("message")
                dead_entity: Optional[Entity] = player_turn_result.get("dead")
                item_added: Optional[Entity] = player_turn_result.get("item_added")
                item_consumed: Optional[Entity] = player_turn_result.get("consumed")
                item_dropped: Optional[Entity] = player_turn_result.get("item_dropped")
                targeting: Optional[Entity] = player_turn_result.get("targeting")
                targeting_cancelled: bool = player_turn_result.get("targeting_cancelled", False)

                if message:
                    game.message_log.add_message(message)

                if targeting_cancelled:
                    game.game_state = game.previous_game_state

                    game.message_log.add_message(Message("Targeting cancelled"))

                if dead_entity:
                    if dead_entity == game.player:
                        message = kill_player(player=dead_entity)
                        game.game_state = GameStates.PLAYER_DEAD
                    else:
                        message = kill_monster(monster=dead_entity)

                    game.message_log.add_message(message)

                if item_added:
                    game.entities.remove(item_added)

                    game.game_state = GameStates.ENEMY_TURN
                    game.camera.fov_update = True

                if item_consumed:
                    game.game_state = GameStates.ENEMY_TURN
                    game.camera.fov_update = True

                if targeting:
                    game.change_state(GameStates.TARGETING)

                    targeting_item: Entity = targeting

                    game.message_log.add_message(targeting_item.item.targeting_message)

                if item_dropped:
                    game.entities.append(item_dropped)

                    game.game_state = GameStates.ENEMY_TURN

            if game.game_state == GameStates.ENEMY_TURN:
                for entity in game.entities[1:]:
                    if entity.ai:
                        enemy_turn_results = entity.ai.take_turn(
                            target=game.player,
                            fov_map=game.fov_map,
                            game_map=game.game_map,
                            entities=game.entities,
                        )

                        for enemy_turn_result in enemy_turn_results:
                            message = enemy_turn_result.get("message")
                            dead_entity = enemy_turn_result.get("dead")

                            if message:
                                game.message_log.add_message(message)

                            if dead_entity:
                                if dead_entity == game.player:
                                    message = kill_player(player=dead_entity)
                                    game.game_state = GameStates.PLAYER_DEAD
                                else:
                                    message = kill_monster(monster=dead_entity)

                                game.message_log.add_message(message)
                                game.camera.fov_update = True

                                if game.game_state == GameStates.PLAYER_DEAD:
                                    break
                        if game.game_state == GameStates.PLAYER_DEAD:
                            break
                else:
                    game.game_state = GameStates.PLAYER_TURN


if __name__ == "__main__":
    main()
    blt.close()
