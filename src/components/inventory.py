from __future__ import annotations

from typing import List, TYPE_CHECKING, Dict

from colors import Colors
from components.entity_component import EntityComponent
from game_messages import Message

if TYPE_CHECKING:
    from components.item import Item


class Inventory(EntityComponent):
    def __init__(self, capacity: int):
        super(Inventory, self).__init__()
        self.capacity: int = capacity
        self.items: List[Item] = []

    def add_item(self, item: Item) -> List[Dict]:
        results = []

        if len(self.items) >= self.capacity:
            results.append({
                "item_added": None,
                "message": Message("You cannot carry any more, your inventory is full", Colors.YELLOW)
            })
        else:
            results.append({
                "item_added": item,
                "message": Message(f"You pick up the {item.name}!", Colors.BLUE)
            })

            self.items.append(item)

        return results
