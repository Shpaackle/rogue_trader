from typing import List, Optional

from bearlibterminal import terminal as blt

from entity import Entity
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

    room_min_size = 10
    room_max_size = 6
    max_rooms = 30

    colors = {
        "dark_wall": blt.color_from_argb(0, 100, 100, 100),
        "dark_ground": blt.color_from_argb(0, 50, 50, 150)
    }

    game_running: bool = True

    player: Entity = Entity(
        position=Point(x=map_width//2, y=map_height//2),
        char="@",
        color=blt.color_from_argb(0, 255, 255, 255)
    )
    npc: Entity = Entity(
        position=Point(x=screen_width // 2 + 2, y=screen_height // 2),
        char="@",
        color=blt.color_from_argb(0, 255, 255, 0)
    )
    entities: List[Entity] = [player, npc]

    # game_map: GameMap = GameMap(width=map_width, height=map_height)
    # game_map.make_cave(map_width, map_height, player)
    # cave_map_settings = {
    #     "first_pass_one": 5,
    #     "first_pass_two": 2,
    #     "second_pass_one": 5,
    #     "second_pass_two": -1
    # }
    map_generator = MapGenerator()
    map_generator.generate_caves(width=map_width, height=map_height)

    game_map: GameMap = map_generator.game_map

    blt.open()
    blt.composition(True)
    blt.set(f"window: size={screen_width}x{screen_height}, title={window_title}")

    while game_running:
        render_all(entities=entities, game_map=game_map, colors=colors,)

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

            if redraw:
                map_generator.generate_caves(width=map_width, height=map_height)
                game_map: GameMap = map_generator.game_map

        blt.clear()


if __name__ == "__main__":
    main()
    blt.close()
