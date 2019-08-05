from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from bearlibterminal import terminal as blt

from camera import Camera
from colors import Colors
from components.fighter import Fighter
from components.inventory import Inventory
from death_functions import kill_monster, kill_player
from entity import Entity, get_blocking_entities_at_location
from fov_functions import initialize_fov, recompute_fov
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
    constants: dict = get_constants()

    game_running: bool = True

    fighter_component: Fighter = Fighter(hp=30, defense=2, power=5)
    inventory_component: Inventory = Inventory(26)
    player: Entity = Entity(
        position=Point(x=0, y=0),
        char="@",
        color=Colors.WHITE,
        name="Player",
        blocks=True,
        render_order=RenderOrder.ACTOR,
        fighter=fighter_component,
        inventory=inventory_component
    )
    entities: List[Entity] = [player]

    map_generator: MapGenerator = MapGenerator(
        map_width=constants["map_width"], map_height=constants["map_height"]
    )

    map_generator.make_map(
        width=constants["map_width"],
        height=constants["map_height"],
        entities=entities,
        min_monsters=constants["min_monsters"],
        max_monsters=constants["max_monsters"],
        max_items=constants["max_items"]
    )
    # map_generator.generate_caves(width=map_width, height=map_height)

    game_map: GameMap = map_generator.game_map

    # fov_update: bool = True

    fov_map: tcod.map.Map = initialize_fov(game_map)

    message_log: MessageLog = MessageLog(constants["message_x"], constants["message_width"], constants["message_height"])

    player.position: Point = map_generator.player_start_point

    camera: Camera = Camera(player=player, width=constants["camera_width"], height=constants["camera_height"])
    blt.open()
    blt.composition(True)
    blt.set(f"window: size={constants['screen_width']}x{constants['screen_height']}, title={constants['window_title']}, cellsize=8x8")
    blt.set("input: filter={keyboard, mouse+}")
    blt.set(f"{constants['map_font']}")
    blt.set(f"{constants['ui_font']}")
    blt.set(f"{constants['bar_font']}")
    blt.set(f"{constants['hover_font']}")

    game_state: GameStates = GameStates.PLAYER_TURN
    previous_game_state: GameStates = game_state

    targeting_item: Optional[Entity] = None

    mouse_position: Point = Point(x=blt.state(blt.TK_MOUSE_X)//2, y=blt.state(blt.TK_MOUSE_Y)//2)

    while game_running:
        if camera.fov_update:
            recompute_fov(
                fov_map, player.position, constants["fov_radius"], constants["fov_light_walls"], constants["fov_algorithm"]
            )
        render_all(
            entities=entities,
            player=player,
            game_map=game_map,
            fov_map=fov_map,
            camera=camera,
            message_log=message_log,
            ui_panel=constants["ui_panel"],
            bar_width=constants["bar_width"],
            mouse_position=mouse_position,
            game_state=game_state
        )

        camera.fov_update = False

        # blt.refresh()

        if blt.has_input():
            terminal_input: int = blt.read()

            mouse_position = Point(x=blt.state(blt.TK_MOUSE_X) // 2, y=blt.state(blt.TK_MOUSE_Y) // 2)
            camera.fov_update = True

            action: dict = handle_keys(terminal_input, game_state)
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
                previous_game_state = game_state
                game_state = GameStates.SHOW_INVENTORY

            if drop_inventory:
                previous_game_state = game_state
                game_state = GameStates.DROP_INVENTORY

            if inventory_index is not None and previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(player.inventory.items):
                item = player.inventory.items[inventory_index]

                if game_state == GameStates.SHOW_INVENTORY:
                    player_turn_results.extend(player.inventory.use(item, entities=entities, fov_map=fov_map))
                elif game_state == GameStates.DROP_INVENTORY:
                    player_turn_results.extend(player.inventory.drop_item(item))

            if game_state == GameStates.TARGETING:
                if left_click:
                    target_position: Point = camera.map_point(left_click)

                    item_use_results = player.inventory.use(targeting_item, entities=entities, fov_map=fov_map, target_position=target_position)
                    player_turn_results.extend(item_use_results)
                elif right_click:
                    player_turn_results.append({"targeting_cancelled": True})

            if exit_action:
                if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
                    game_state = GameStates.PLAYER_TURN
                elif game_state == GameStates.TARGETING:
                    player_turn_results.append({"targeting_cancelled": True})

                else:
                    game_running = False

            # player_turn_results = []

            if movement and game_state == GameStates.PLAYER_TURN:
                destination = player.position + movement
                if not game_map.is_blocked(destination):
                    target = get_blocking_entities_at_location(
                        entities=entities, destination=destination
                    )

                    if target:
                        attack_results = player.fighter.attack(target=target)
                        player_turn_results.extend(attack_results)
                        camera.fov_update = True
                    else:
                        player.move(movement)
                        camera.recenter()

                        # fov_update = True

                    game_state = GameStates.ENEMY_TURN
            elif pickup and game_state == GameStates.PLAYER_TURN:
                for entity in entities:
                    if entity.item and entity.position == player.position:
                        pickup_results = player.inventory.add_item(entity)
                        player_turn_results.extend(pickup_results)

                        break
                else:
                    message_log.add_message(Message("There is nothing here to pick up."))

            for player_turn_result in player_turn_results:
                message = player_turn_result.get("message")
                dead_entity = player_turn_result.get("dead")
                item_added = player_turn_result.get("item_added")
                item_consumed = player_turn_result.get("consumed")
                item_dropped = player_turn_result.get("item_dropped")
                targeting = player_turn_result.get("targeting")
                targeting_cancelled: bool = player_turn_result.get("targeting_cancelled", False)

                if message:
                    message_log.add_message(message)

                if targeting_cancelled:
                    game_state = previous_game_state

                    message_log.add_message(Message("Targeting cancelled"))

                if dead_entity:
                    if dead_entity == player:
                        message = kill_player(player=dead_entity)
                        game_state = GameStates.PLAYER_DEAD
                    else:
                        message = kill_monster(monster=dead_entity)

                    message_log.add_message(message)

                if item_added:
                    entities.remove(item_added)

                    game_state = GameStates.ENEMY_TURN
                    camera.fov_update = True

                if item_consumed:
                    game_state = GameStates.ENEMY_TURN
                    camera.fov_update = True

                if targeting:
                    previous_game_state = game_state
                    game_state = GameStates.TARGETING

                    targeting_item: Entity = targeting

                    message_log.add_message(targeting_item.item.targeting_message)

                if item_dropped:
                    entities.append(item_dropped)

                    game_state = GameStates.ENEMY_TURN

            if game_state == GameStates.ENEMY_TURN:
                for entity in entities[1:]:
                    if entity.ai:
                        enemy_turn_results = entity.ai.take_turn(
                            target=player,
                            fov_map=fov_map,
                            game_map=game_map,
                            entities=entities,
                        )

                        for enemy_turn_result in enemy_turn_results:
                            message = enemy_turn_result.get("message")
                            dead_entity = enemy_turn_result.get("dead")

                            if message:
                                message_log.add_message(message)

                            if dead_entity:
                                if dead_entity == player:
                                    message = kill_player(player=dead_entity)
                                    game_state = GameStates.PLAYER_DEAD
                                else:
                                    message = kill_monster(monster=dead_entity)

                                message_log.add_message(message)
                                camera.fov_update = True

                                if game_state == GameStates.PLAYER_DEAD:
                                    break
                        if game_state == GameStates.PLAYER_DEAD:
                            break
                else:
                    game_state = GameStates.PLAYER_TURN


if __name__ == "__main__":
    main()
    blt.close()
