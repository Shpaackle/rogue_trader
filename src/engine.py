from __future__ import annotations

from typing import List, Optional

from bearlibterminal import terminal as blt

from camera import Camera
from colors import Color
from components.fighter import Fighter
from death_functions import kill_monster, kill_player
from entity import Entity, get_blocking_entities_at_location
from fov_functions import initialize_fov, recompute_fov
from game_states import GameStates
from input_handlers import handle_keys
from map_objects.game_map import GameMap
from map_objects.map_generator import MapGenerator
from map_objects import Point
from render_functions import render_all, RenderOrder


def main():
    screen_width: int = 120
    screen_height: int = 45
    window_title: str = "Rogue Trader"

    map_width: int = 80
    map_height: int = 40

    room_min_size: int = 10
    room_max_size: int = 6
    max_rooms: int = 30
    max_monsters: int = 10
    min_monsters: int = 3

    fov_algorithm: int = 0
    fov_light_walls: bool = True
    fov_radius: int = 10

    colors: dict = {
        "dark_wall": blt.color_from_argb(0, 100, 100, 100),
        "dark_ground": blt.color_from_argb(0, 50, 50, 150),
        "light_wall": blt.color_from_argb(0, 130, 100, 50),
        "light_ground": blt.color_from_argb(0, 200, 180, 50),
    }

    game_running: bool = True

    fighter_component: Fighter = Fighter(hp=30, defense=2, power=5)
    player: Entity = Entity(
        position=Point(x=0, y=0),
        char="@",
        color=Color.WHITE,
        name="Player",
        blocks=True,
        render_order=RenderOrder.ACTOR,
        fighter=fighter_component,
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
    )
    # map_generator.generate_caves(width=map_width, height=map_height)

    game_map: GameMap = map_generator.game_map

    # fov_update: bool = True

    fov_map = initialize_fov(game_map)

    player.position = map_generator.player_start_point

    camera = Camera(player=player, width=map_width, height=map_height)
    blt.open()
    blt.composition(True)
    blt.set(f"window: size={screen_width}x{screen_height}, title={window_title}")

    game_state = GameStates.PLAYER_TURN

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
            camera=camera
        )

        camera.fov_update = False

        # blt.refresh()

        if blt.has_input():
            terminal_input: int = blt.read()

            action: dict = handle_keys(terminal_input)

            exit_game: bool = action.get("exit", False)
            movement: Optional[Point] = action.get("move", None)

            if exit_game:
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

            for player_turn_result in player_turn_results:
                message = player_turn_result.get("message")
                dead_entity = player_turn_result.get("dead")

                if message:
                    print(message)

                if dead_entity:
                    if dead_entity == player:
                        message, game_state = kill_player(player=dead_entity)
                    else:
                        message = kill_monster(monster=dead_entity)

                    print(message)

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
                                print(message)

                            if dead_entity:
                                if dead_entity == player:
                                    message, game_state = kill_player(player=dead_entity)
                                else:
                                    message = kill_monster(monster=dead_entity)

                                print(message)
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
