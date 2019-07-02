from bearlibterminal import terminal as blt

from input_handlers import handle_keys


def main():
    screen_width: int = 120
    screen_height: int = 45
    window_title: str = "Rogue Trader"

    map_width: int = 80
    map_height: int = 40

    game_running: bool = True

    player_x: int = screen_width // 2
    player_y: int = screen_height // 2

    blt.open()
    blt.composition(True)
    blt.set(f"window: size={screen_width}x{screen_height}, title={window_title}")

    while game_running:
        blt.printf(player_x, player_y, "@")

        blt.refresh()

        if blt.has_input():
            terminal_input: int = blt.read()

            action = handle_keys(terminal_input)

            exit_game = action.get("exit")
            move = action.get("move")

            if exit_game:
                game_running = False

            if move:
                dx, dy = move

                player_x += dx
                player_y += dy

        blt.clear()


if __name__ == "__main__":
    main()
    blt.close()
