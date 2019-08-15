from __future__ import annotations

from typing import Optional, TYPE_CHECKING, Dict, List

from bearlibterminal import terminal as blt

from camera import Camera
from colors import Colors
from constants import CONSTANTS
from death_functions import kill_monster, kill_player
from entity import Entity, get_blocking_entities_at_location
from fov_functions import initialize_fov, recompute_fov
from game import Game
from game_messages import Message
from game_states import GameStates
from input_handlers import handle_keys, handle_main_menu, handle_mouse
from map_objects import Point
from menus import main_menu, message_box
from render_functions import render_all

if TYPE_CHECKING:
    import tcod.map


def play_game(game: Game):

    game.fov_map: tcod.map.Map = initialize_fov(game.game_map)

    game.game_state: GameStates = GameStates.PLAYER_TURN
    game.previous_state: GameStates = game.game_state

    game.camera: Camera = Camera(
        player=game.player, width=CONSTANTS.camera_width, height=CONSTANTS.camera_height
    )
    game.camera.fov_update: bool = True

    targeting_item: Optional[Entity] = None

    mouse_position: Point = Point(
        x=blt.state(blt.TK_MOUSE_X) // 2, y=blt.state(blt.TK_MOUSE_Y) // 2
    )

    while game.game_running:
        if game.camera.fov_update:
            recompute_fov(
                fov_map=game.fov_map,
                point=game.player.position,
                radius=CONSTANTS.fov_radius,
                light_walls=CONSTANTS.fov_light_walls,
                algorithm=CONSTANTS.fov_algorithm,
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
            game_state=game.game_state,
        )

        game.camera.fov_update = False

        if blt.has_input():
            terminal_input: int = blt.read()
            mouse_position: Point = Point(
                x=blt.state(blt.TK_MOUSE_X) // 2, y=blt.state(blt.TK_MOUSE_Y) // 2
            )

            action: dict = handle_keys(key=terminal_input, game_state=game.game_state)
            mouse_action: dict = handle_mouse(key=terminal_input)

            movement: Optional[Point] = action.get("move")
            wait: bool = action.get("wait", False)
            pickup: bool = action.get("pickup", False)
            show_inventory: bool = action.get("show_inventory", False)
            drop_inventory: bool = action.get("drop_inventory", False)
            inventory_index: Optional[int] = action.get("inventory_index")
            take_stairs: bool = action.get("take_stairs", False)
            level_up: str = action.get("level_up")
            show_character_screen: bool = action.get("show_character_screen", False)
            exit_action: bool = action.get("exit", False)

            left_click: Point = mouse_action.get("left_click")
            right_click: Point = mouse_action.get("right_click")

            player_turn_results: List = []

            if movement and game.game_state == GameStates.PLAYER_TURN:
                destination = game.player.position + movement

                if not game.game_map.is_blocked(destination):
                    target = get_blocking_entities_at_location(
                        entities=game.entities, destination=destination
                    )

                    if target:
                        attack_results = game.player.fighter.attack(target=target)
                        player_turn_results.extend(attack_results)
                    else:
                        game.player.move(movement)
                        game.camera.recenter()

                    game.change_state(GameStates.ENEMY_TURN)
            elif wait:
                game.change_state(GameStates.ENEMY_TURN)
            elif pickup and game.game_state == GameStates.PLAYER_TURN:
                for entity in game.entities:
                    if entity.item and entity.position == game.player.position:
                        pickup_results = game.player.inventory.add_item(entity)
                        player_turn_results.extend(pickup_results)

                        break
                else:
                    game.message_log.add_message(
                        Message("There is nothing here to pick up.")
                    )

            if show_inventory:
                game.change_state(GameStates.SHOW_INVENTORY)

            if drop_inventory:
                game.change_state(GameStates.DROP_INVENTORY)

            if (
                inventory_index is not None
                and game.previous_state != GameStates.PLAYER_DEAD
                and inventory_index < len(game.player.inventory.items)
            ):
                item = game.player.inventory.items[inventory_index]

                if game.game_state == GameStates.SHOW_INVENTORY:
                    player_turn_results.extend(
                        game.player.inventory.use(
                            item, entities=game.entities, fov_map=game.fov_map
                        )
                    )
                elif game.game_state == GameStates.DROP_INVENTORY:
                    player_turn_results.extend(game.player.inventory.drop_item(item))

            if take_stairs and game.game_state == GameStates.PLAYER_TURN:
                for entity in game.entities:
                    if entity.stairs and entity.position == game.player.position:
                        game.next_floor()
                        game.fov_map = initialize_fov(game.game_map)
                        game.camera.fov_update = True

                        break

                else:
                    game.message_log.add_message(Message("There are no stairs here.", Colors.YELLOW))

            if level_up:
                if level_up == "hp":
                    game.player.fighter.max_hp += 20
                    game.player.fighter.hp += 20
                elif level_up == "str":
                    game.player.fighter.power += 1
                elif level_up == "dex":
                    game.player.fighter.defense += 1

                game.change_state(game.previous_state)

            if show_character_screen:
                game.change_state(GameStates.CHARACTER_SCREEN)

            if game.game_state == GameStates.TARGETING:
                if left_click:
                    target_position: Point = game.camera.map_point(left_click)

                    item_use_results = game.player.inventory.use(
                        targeting_item,
                        entities=game.entities,
                        fov_map=game.fov_map,
                        target_position=target_position,
                    )
                    player_turn_results.extend(item_use_results)
                elif right_click:
                    player_turn_results.append({"targeting_cancelled": True})

            if exit_action:
                if game.game_state in (
                    GameStates.SHOW_INVENTORY,
                    GameStates.DROP_INVENTORY,
                    GameStates.CHARACTER_SCREEN
                ):
                    game.change_state(GameStates.PLAYER_TURN)
                elif game.game_state == GameStates.TARGETING:
                    player_turn_results.append({"targeting_cancelled": True})
                else:
                    game.save_game()
                    game.game_running = False

            for player_turn_result in player_turn_results:
                message: Optional[Message] = player_turn_result.get("message")
                dead_entity: Optional[Entity] = player_turn_result.get("dead")
                item_added: Optional[Entity] = player_turn_result.get("item_added")
                item_consumed: Optional[Entity] = player_turn_result.get("consumed")
                item_dropped: Optional[Entity] = player_turn_result.get("item_dropped")
                targeting: Optional[Entity] = player_turn_result.get("targeting")
                xp: Optional[int] = player_turn_result.get("xp")
                targeting_cancelled: bool = player_turn_result.get(
                    "targeting_cancelled", False
                )

                if message:
                    game.message_log.add_message(message)

                if targeting_cancelled:
                    game.game_state = game.previous_state

                    game.message_log.add_message(Message("Targeting cancelled"))

                if xp:
                    leveled_up = game.player.level.add_xp(xp=xp)
                    game.message_log.add_message(Message(f"You gain {xp} experience points."))

                    if leveled_up:
                        game.message_log.add_message(Message(f"Your battle skills grow stronger! You reached level {game.player.level.current_level}!", Colors.YELLOW))
                        game.change_state(GameStates.LEVEL_UP)

                if dead_entity:
                    if dead_entity == game.player:
                        message = kill_player(player=dead_entity)
                        game.change_state(GameStates.PLAYER_DEAD)
                    else:
                        message = kill_monster(monster=dead_entity)

                    game.message_log.add_message(message)

                if item_added:
                    game.entities.remove(item_added)

                    game.change_state(GameStates.ENEMY_TURN)
                    game.camera.fov_update = True

                if item_consumed:
                    game.change_state(GameStates.ENEMY_TURN)

                if targeting:
                    game.change_state(GameStates.TARGETING)

                    targeting_item: Entity = targeting

                    game.message_log.add_message(targeting_item.item.targeting_message)

                if item_dropped:
                    game.entities.append(item_dropped)

                    game.change_state(GameStates.ENEMY_TURN)

            if game.game_state == GameStates.ENEMY_TURN:
                for entity in game.entities:
                    if entity.ai:
                        enemy_turn_results = entity.ai.take_turn(
                            target=game.player,
                            fov_map=game.fov_map,
                            game_map=game.game_map,
                            entities=game.entities,
                        )

                        for enemy_turn_result in enemy_turn_results:
                            message: Optional[Message] = enemy_turn_result.get(
                                "message"
                            )
                            dead_entity = enemy_turn_result.get("dead")

                            if message:
                                game.message_log.add_message(message)

                            if dead_entity:
                                if dead_entity == game.player:
                                    message = kill_player(player=dead_entity)
                                    game.change_state(GameStates.PLAYER_DEAD)
                                else:
                                    message = kill_monster(monster=dead_entity)
                                game.message_log.add_message(message)
                                if game.game_state == GameStates.PLAYER_DEAD:
                                    break
                else:
                    game.change_state(GameStates.PLAYER_TURN)


def main():
    game = Game()
    show_load_error_message = False

    game.game_state: GameStates = GameStates.MAIN_MENU
    game.previous_state: GameStates = game.game_state

    blt.open()
    blt.composition(True)
    blt.set(
        f"window: size={CONSTANTS.screen_width}x{CONSTANTS.screen_height}, title={CONSTANTS.window_title}, cellsize=8x8"
    )
    blt.set("input: filter={keyboard, mouse+}")
    blt.set(f"{CONSTANTS.map_font}")
    blt.set(f"{CONSTANTS.ui_font}")
    blt.set(f"{CONSTANTS.bar_font}")
    blt.set(f"{CONSTANTS.hover_font}")

    while game.game_running:
        if game.game_state == GameStates.MAIN_MENU:

            blt.clear()

            if show_load_error_message:
                message_box(
                    header="No save game to load",
                    width=50,
                    screen_width=CONSTANTS.screen_width,
                    screen_height=CONSTANTS.screen_height,
                )

            main_menu(CONSTANTS.camera_width)
            blt.refresh()

            if blt.has_input():

                terminal_input = blt.read()
                print(terminal_input)
                action = handle_main_menu(terminal_input)

                new_game: bool = action.get("new_game", False)
                load_saved_game: bool = action.get("load_game", False)
                exit_game: bool = action.get("exit_game", False)

                if show_load_error_message and (
                    new_game or load_saved_game or exit_game
                ):
                    show_load_error_message = False
                elif new_game:
                    game = game.new_game()
                    game.map_generator.make_map(
                        width=CONSTANTS.map_width,
                        height=CONSTANTS.map_height,
                        entities=game.entities,
                        min_monsters=CONSTANTS.min_monsters,
                        max_monsters=CONSTANTS.max_monsters,
                        max_items=CONSTANTS.max_items,
                    )
                    game.game_state = GameStates.PLAYER_TURN
                    game.player.position = game.map_generator.player_start_point

                elif load_saved_game:
                    try:
                        game = game.load_game()
                    except FileNotFoundError:
                        show_load_error_message = True
                elif exit_game:
                    break
        else:
            blt.clear()
            play_game(game)

            game.game_state = GameStates.MAIN_MENU


# def main_():
#     game = Game()
#
#     game.map_generator.make_map(
#         width=CONSTANTS.map_width,
#         height=CONSTANTS.map_height,
#         entities=game.entities,
#         min_monsters=CONSTANTS.min_monsters,
#         max_monsters=CONSTANTS.max_monsters,
#         max_items=CONSTANTS.max_items,
#     )
#     # map_generator.generate_caves(width=map_width, height=map_height)
#
#     # game_map: GameMap = map_generator.game_map
#
#     # fov_update: bool = True
#
#     game.fov_map: tcod.map.Map = initialize_fov(game.game_map)
#
#     # message_log: MessageLog = MessageLog(constants["message_x"], constants["message_width"], constants["message_height"])
#
#     game.player.position: Point = game.map_generator.player_start_point
#
#     game.camera: Camera = Camera(
#         player=game.player, width=CONSTANTS.camera_width, height=CONSTANTS.camera_height
#     )
#     blt.open()
#     blt.composition(True)
#     blt.set(
#         f"window: size={CONSTANTS.screen_width}x{CONSTANTS.screen_height}, title={CONSTANTS.window_title}, cellsize=8x8"
#     )
#     blt.set("input: filter={keyboard, mouse+}")
#     blt.set(f"{CONSTANTS.map_font}")
#     blt.set(f"{CONSTANTS.ui_font}")
#     blt.set(f"{CONSTANTS.bar_font}")
#     blt.set(f"{CONSTANTS.hover_font}")
#
#     game.game_state: GameStates = GameStates.PLAYER_TURN
#     game.previous_game_state: GameStates = game.game_state
#
#     targeting_item: Optional[Entity] = None
#
#     mouse_position: Point = Point(
#         x=blt.state(blt.TK_MOUSE_X) // 2, y=blt.state(blt.TK_MOUSE_Y) // 2
#     )
#
#     while game.game_running:
#
#         if game.camera.fov_update:
#             recompute_fov(
#                 game.fov_map,
#                 game.player.position,
#                 CONSTANTS.fov_radius,
#                 CONSTANTS.fov_light_walls,
#                 CONSTANTS.fov_algorithm,
#             )
#         render_all(
#             entities=game.entities,
#             player=game.player,
#             game_map=game.game_map,
#             fov_map=game.fov_map,
#             camera=game.camera,
#             message_log=game.message_log,
#             ui_panel=CONSTANTS.ui_panel,
#             bar_width=CONSTANTS.bar_width,
#             mouse_position=mouse_position,
#             game_state=game.game_state,
#         )
#
#         game.camera.fov_update = False
#
#         # blt.refresh()
#
#         if blt.has_input():
#             terminal_input: int = blt.read()
#
#             mouse_position = Point(
#                 x=blt.state(blt.TK_MOUSE_X) // 2, y=blt.state(blt.TK_MOUSE_Y) // 2
#             )
#             game.camera.fov_update = True
#
#             action: dict = handle_keys(terminal_input, game.game_state)
#             mouse_action: dict = handle_mouse(terminal_input, mouse_position)
#
#             movement: Optional[Point] = action.get("move", None)
#             pickup: bool = action.get("pickup", False)
#             show_inventory: bool = action.get("show_inventory", False)
#             drop_inventory: bool = action.get("drop_inventory", False)
#             inventory_index: Optional[int] = action.get("inventory_index", None)
#             exit_action: bool = action.get("exit", False)
#
#             left_click = mouse_action.get("left_click")
#             right_click = mouse_action.get("right_click")
#
#             player_turn_results = []
#
#             if show_inventory:
#                 game.change_state(GameStates.SHOW_INVENTORY)
#
#             if drop_inventory:
#                 game.change_state(GameStates.DROP_INVENTORY)
#
#             if (
#                 inventory_index is not None
#                 and game.previous_game_state != GameStates.PLAYER_DEAD
#                 and inventory_index < len(game.player.inventory.items)
#             ):
#                 item = game.player.inventory.items[inventory_index]
#
#                 if game.game_state == GameStates.SHOW_INVENTORY:
#                     player_turn_results.extend(
#                         game.player.inventory.use(
#                             item, entities=game.entities, fov_map=game.fov_map
#                         )
#                     )
#                 elif game.game_state == GameStates.DROP_INVENTORY:
#                     player_turn_results.extend(game.player.inventory.drop_item(item))
#
#             if game.game_state == GameStates.TARGETING:
#                 if left_click:
#                     target_position: Point = game.camera.map_point(left_click)
#
#                     item_use_results = game.player.inventory.use(
#                         targeting_item,
#                         entities=game.entities,
#                         fov_map=game.fov_map,
#                         target_position=target_position,
#                     )
#                     player_turn_results.extend(item_use_results)
#                 elif right_click:
#                     player_turn_results.append({"targeting_cancelled": True})
#
#             if exit_action:
#                 if game.game_state in (
#                     GameStates.SHOW_INVENTORY,
#                     GameStates.DROP_INVENTORY,
#                 ):
#                     game.game_state = GameStates.PLAYER_TURN
#                 elif game.game_state == GameStates.TARGETING:
#                     player_turn_results.append({"targeting_cancelled": True})
#
#                 else:
#                     game.game_running = False
#
#             # player_turn_results = []
#
#             if movement and game.game_state == GameStates.PLAYER_TURN:
#                 destination = game.player.position + movement
#                 if not game.game_map.is_blocked(destination):
#                     target = get_blocking_entities_at_location(
#                         entities=game.entities, destination=destination
#                     )
#
#                     if target:
#                         attack_results = game.player.fighter.attack(target=target)
#                         player_turn_results.extend(attack_results)
#                         game.camera.fov_update = True
#                     else:
#                         game.player.move(movement)
#                         game.camera.recenter()
#
#                         # fov_update = True
#
#                     game.change_state(GameStates.ENEMY_TURN)
#             elif pickup and game.game_state == GameStates.PLAYER_TURN:
#                 for entity in game.entities:
#                     if entity.item and entity.position == game.player.position:
#                         pickup_results = game.player.inventory.add_item(entity)
#                         player_turn_results.extend(pickup_results)
#
#                         break
#                 else:
#                     game.message_log.add_message(
#                         Message("There is nothing here to pick up.")
#                     )
#
#             for player_turn_result in player_turn_results:
#                 message: Optional[Message] = player_turn_result.get("message")
#                 dead_entity: Optional[Entity] = player_turn_result.get("dead")
#                 item_added: Optional[Entity] = player_turn_result.get("item_added")
#                 item_consumed: Optional[Entity] = player_turn_result.get("consumed")
#                 item_dropped: Optional[Entity] = player_turn_result.get("item_dropped")
#                 targeting: Optional[Entity] = player_turn_result.get("targeting")
#                 targeting_cancelled: bool = player_turn_result.get(
#                     "targeting_cancelled", False
#                 )
#
#                 if message:
#                     game.message_log.add_message(message)
#
#                 if targeting_cancelled:
#                     game.game_state = game.previous_game_state
#
#                     game.message_log.add_message(Message("Targeting cancelled"))
#
#                 if dead_entity:
#                     if dead_entity == game.player:
#                         message = kill_player(player=dead_entity)
#                         game.game_state = GameStates.PLAYER_DEAD
#                     else:
#                         message = kill_monster(monster=dead_entity)
#
#                     game.message_log.add_message(message)
#
#                 if item_added:
#                     game.entities.remove(item_added)
#
#                     game.game_state = GameStates.ENEMY_TURN
#                     game.camera.fov_update = True
#
#                 if item_consumed:
#                     game.game_state = GameStates.ENEMY_TURN
#                     game.camera.fov_update = True
#
#                 if targeting:
#                     game.change_state(GameStates.TARGETING)
#
#                     targeting_item: Entity = targeting
#
#                     game.message_log.add_message(targeting_item.item.targeting_message)
#
#                 if item_dropped:
#                     game.entities.append(item_dropped)
#
#                     game.game_state = GameStates.ENEMY_TURN
#
#             if game.game_state == GameStates.ENEMY_TURN:
#                 for entity in game.entities[1:]:
#                     if entity.ai:
#                         enemy_turn_results = entity.ai.take_turn(
#                             target=game.player,
#                             fov_map=game.fov_map,
#                             game_map=game.game_map,
#                             entities=game.entities,
#                         )
#
#                         for enemy_turn_result in enemy_turn_results:
#                             message = enemy_turn_result.get("message")
#                             dead_entity = enemy_turn_result.get("dead")
#
#                             if message:
#                                 game.message_log.add_message(message)
#
#                             if dead_entity:
#                                 if dead_entity == game.player:
#                                     message = kill_player(player=dead_entity)
#                                     game.game_state = GameStates.PLAYER_DEAD
#                                 else:
#                                     message = kill_monster(monster=dead_entity)
#
#                                 game.message_log.add_message(message)
#                                 game.camera.fov_update = True
#
#                                 if game.game_state == GameStates.PLAYER_DEAD:
#                                     break
#                         if game.game_state == GameStates.PLAYER_DEAD:
#                             break
#                 else:
#                     game.game_state = GameStates.PLAYER_TURN


if __name__ == "__main__":
    main()
    blt.close()
