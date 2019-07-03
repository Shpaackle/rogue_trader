from typing import List

from bearlibterminal import terminal as blt

from entity import Entity
from input_handlers import handle_keys
from map_objects import GameMap
from map_objects import Point
from render_functions import render_all


def main():
    screen_width: int = 120
    screen_height: int = 45
    window_title: str = "Rogue Trader"

    map_width: int = 80
    map_height: int = 40

    colors = {
        "dark_wall": blt.color_from_argb(0, 0, 0, 100),
        "dark_ground": blt.color_from_argb(0, 50, 50, 150)
    }

    game_running: bool = True

    game_map: GameMap = GameMap(width=map_width, height=map_height)

    player: Entity = Entity(
        position=Point(x=screen_width//2, y=screen_height//2),
        char="@",
        color=blt.color_from_argb(0, 255, 255, 255)
    )
    npc: Entity = Entity(
        position=Point(x=screen_width // 2 + 2, y=screen_height // 2),
        char="@",
        color=blt.color_from_argb(0, 255, 255, 0)
    )
    entities: List[Entity] = [player, npc]

    blt.open()
    blt.composition(True)
    blt.set(f"window: size={screen_width}x{screen_height}, title={window_title}")

    while game_running:
        render_all(entities=entities, game_map=game_map, colors=colors)

        blt.refresh()

        if blt.has_input():
            terminal_input: int = blt.read()

            action: dict = handle_keys(terminal_input)

            exit_game: bool = action.get("exit", False)
            movement: Point = action.get("move")

            if exit_game:
                game_running = False

            if movement:
                if not game_map.is_blocked(player.x + movement.x, player.y + movement.y):
                    player.move(movement)

        blt.clear()


if __name__ == "__main__":
    main()
    blt.close()
