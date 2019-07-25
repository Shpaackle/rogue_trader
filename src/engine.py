from typing import List, Optional

from bearlibterminal import terminal as blt

from colors import Color
from entity import Entity, get_blocking_entities_at_location
from fov_functions import initialize_fov, recompute_fov
from game_states import GameStates
from input_handlers import handle_keys
from map_objects.game_map import GameMap
from map_objects.map_generator import MapGenerator
from map_objects import Point
from render_functions import render_all


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

    player: Entity = Entity(
        position=Point(x=0, y=0), char="@", color=Color.WHITE, name="Player", blocks=True
    )
    entities: List[Entity] = [player]

    map_generator: MapGenerator = MapGenerator(
        map_width=map_width, map_height=map_height
    )

    map_generator.make_map(width=map_width, height=map_height, entities=entities, min_monsters=min_monsters, max_monsters=max_monsters)
    # map_generator.generate_caves(width=map_width, height=map_height)

    game_map: GameMap = map_generator.game_map

    fov_update: bool = True

    fov_map = initialize_fov(game_map)

    player.position = map_generator.player_start_point

    blt.open()
    blt.composition(True)
    blt.set(f"window: size={screen_width}x{screen_height}, title={window_title}")

    game_state = GameStates.PLAYER_TURN

    while game_running:
        if fov_update:
            recompute_fov(
                fov_map, player.position, fov_radius, fov_light_walls, fov_algorithm
            )
        render_all(
            entities=entities,
            game_map=game_map,
            fov_map=fov_map,
            fov_update=fov_update,
            colors=colors,
        )

        fov_update = False

        # blt.refresh()

        if blt.has_input():
            terminal_input: int = blt.read()

            action: dict = handle_keys(terminal_input)

            exit_game: bool = action.get("exit", False)
            movement: Optional[Point] = action.get("move", None)

            if exit_game:
                game_running = False

            if movement and game_state == GameStates.PLAYER_TURN:
                destination = player.position + movement
                if not game_map.is_blocked(destination):
                    target = get_blocking_entities_at_location(entities=entities, destination=destination)

                    if target:
                        blt.printf(2, 42, f"You kick the {target.name} in the shins, much to its annoyance!")

                    else:
                        player.move(movement)

                    fov_update = True

                    game_state = GameStates.ENEMY_TURN

            if game_state == GameStates.ENEMY_TURN:
                y = 1
                for entity in entities[1:]:
                    blt.printf(x=83, y=y, s=f"The {entity.name} ponders the meaning of its existence.")
                    y += 1

                game_state = GameStates.PLAYER_TURN


if __name__ == "__main__":
    main()
    blt.close()
