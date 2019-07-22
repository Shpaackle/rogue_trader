from typing import List, Optional

from bearlibterminal import terminal as blt

from entity import Entity
from fov_functions import initialize_fov, recompute_fov
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
        position=Point(x=0, y=0), char="@", color=blt.color_from_argb(0, 255, 255, 255)
    )
    npc: Entity = Entity(
        position=Point(x=map_width // 2, y=map_height // 2),
        char="@",
        color=blt.color_from_argb(0, 255, 255, 0),
    )
    entities: List[Entity] = [player, npc]

    map_generator: MapGenerator = MapGenerator(
        map_width=map_width, map_height=map_height
    )
    map_generator.generate_caves(width=map_width, height=map_height)

    game_map: GameMap = map_generator.game_map

    fov_update: bool = True

    fov_map = initialize_fov(game_map)

    player.position = map_generator.player_start_point

    blt.open()
    blt.composition(True)
    blt.set(f"window: size={screen_width}x{screen_height}, title={window_title}")

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

        blt.refresh()

        if blt.has_input():
            terminal_input: int = blt.read()

            action: dict = handle_keys(terminal_input)

            exit_game: bool = action.get("exit", False)
            movement: Optional[Point] = action.get("move", None)
            redraw: bool = action.get("redraw", False)

            if exit_game:
                game_running = False

            if movement:
                point = player.position + movement
                if not game_map.is_blocked(point):
                    player.move(movement)

                    fov_recompute = True

            if redraw:
                map_generator.generate_caves(width=map_width, height=map_height)
                game_map: GameMap = map_generator.game_map
                player.position = map_generator.player_start_point

        blt.clear()


if __name__ == "__main__":
    main()
    blt.close()
