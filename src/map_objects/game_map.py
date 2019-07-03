from bearlibterminal import terminal as blt
import tcod
from tcod.map import Map


class GameMap(Map):
    def __init__(self, width: int, height: int):
        super(GameMap, self).__init__(width=width, height=height, order="F")

        self.transparent[:] = True
        self.walkable[:] = True

        self.walkable[30:33, 8] = False

    def is_blocked(self, x: int, y: int) -> bool:
        if not self.walkable[x, y]:
            return True

        return False

    def render(self, colors):
        for y in range(self.height):
            for x in range(self.width):
                wall = self.is_blocked(x, y)

                if wall:
                    blt.printf(x=x, y=y, s=f"[color={colors.get('dark_wall')}]#[/color]")
                else:
                    blt.printf(x=x, y=y, s=f"[color={colors.get('dark_ground')}].[/color]")
