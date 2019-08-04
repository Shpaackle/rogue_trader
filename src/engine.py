from __future__ import annotations

from typing import List, Optional

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
from input_handlers import handle_keys
from map_objects.game_map import GameMap
from map_objects.map_generator import MapGenerator
from map_objects import Point
from rect import Rect
from render_functions import render_all, RenderOrder


def main():
    screen_width: int = 120 * 2
    screen_height: int = 45 * 2
    window_title: str = "Rogue Trader"

    map_font = "map font: mplus-1p-bold.ttf, size=12, spacing=2x2"
    ui_font = "ui_font font: mplus-1p-bold.ttf, size=10"
    bar_font = "bar font: mplus-1p-bold.ttf, size=6, spacing=2x2"
    hover_font = "hover font: mplus-1p-bold.ttf, size=6"

    map_width: int = 80
    map_height: int = 80
    camera_width: int = 65
    camera_height: int = 33

    bar_width: int = 20
    panel_height: int = 12
    panel_y = screen_height - (panel_height * 2)
    ui_panel: Rect = Rect(position=Point(x=0, y=panel_y), width=screen_width, height=panel_height*2)

    message_x = (bar_width + 2) * 2
    message_width = screen_width - ((bar_width - 2) * 2)
    message_height = (panel_height - 1)

    room_min_size: int = 10
    room_max_size: int = 6
    max_rooms: int = 30
    max_monsters: int = 15
    min_monsters: int = 5
    max_items: int = 15

    fov_algorithm: int = 0
    fov_light_walls: bool = True
    fov_radius: int = 10

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
        map_width=map_width, map_height=map_height
    )

    map_generator.make_map(
        width=map_width,
        height=map_height,
        entities=entities,
        min_monsters=min_monsters,
        max_monsters=max_monsters,
        max_items=max_items
    )
    # map_generator.generate_caves(width=map_width, height=map_height)

    game_map: GameMap = map_generator.game_map

    # fov_update: bool = True

    fov_map = initialize_fov(game_map)

    message_log = MessageLog(message_x, message_width, message_height)

    player.position = map_generator.player_start_point

    camera = Camera(player=player, width=camera_width, height=camera_height)
    blt.open()
    blt.composition(True)
    blt.set(f"window: size={screen_width}x{screen_height}, title={window_title}, cellsize=8x8")
    blt.set("input: filter={keyboard, mouse+}")
    blt.set(f"{map_font}")
    blt.set(f"{ui_font}")
    blt.set(f"{bar_font}")
    blt.set(f"{hover_font}")

    game_state = GameStates.PLAYER_TURN
    previous_game_state = game_state
    mouse_position = Point(x=blt.state(blt.TK_MOUSE_X)//2, y=blt.state(blt.TK_MOUSE_Y)//2)

    while game_running:
        if camera.fov_update:
            recompute_fov(
                fov_map, player.position, fov_radius, fov_light_walls, fov_algorithm
            )
        render_all(
            entities=entities,
            player=player,
            game_map=game_map,
            fov_map=fov_map,
            camera=camera,
            message_log=message_log,
            ui_panel=ui_panel,
            bar_width=bar_width,
            mouse_position=mouse_position,
            game_state=game_state
        )

        camera.fov_update = False

        # blt.refresh()

        if blt.has_input():
            terminal_input: int = blt.read()

            mouse_position = Point(x=blt.state(blt.TK_MOUSE_X) // 2, y=blt.state(blt.TK_MOUSE_Y) // 2)
            camera.fov_update = True

            action: dict = handle_keys(terminal_input)

            movement: Optional[Point] = action.get("move", None)
            pickup: bool = action.get("pickup", False)
            show_inventory: bool = action.get("show_inventory", False)
            exit_game: bool = action.get("exit", False)

            if show_inventory:
                previous_game_state = game_state
                game_state = GameStates.SHOW_INVENTORY

            if exit_game:
                if game_state == GameStates.SHOW_INVENTORY:
                    game_state = previous_game_state
                else:
                    game_running = False

            player_turn_results = []

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

                if message:
                    message_log.add_message(message)

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
