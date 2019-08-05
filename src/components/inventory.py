from __future__ import annotations

from typing import List, TYPE_CHECKING

from colors import Colors
from components.entity_component import EntityComponent
from game_messages import Message

if TYPE_CHECKING:
    from components.item import Item
    from entity import Entity
    from map_objects import Point


class Inventory(EntityComponent):
    def __init__(self, capacity: int):
        super(Inventory, self).__init__()
        self.capacity: int = capacity
        self.items: List[Entity] = []

    def add_item(self, item: Entity) -> List[dict]:
        results = []

        if len(self.items) >= self.capacity:
            results.append({
                "item_added": None,
                "message": Message("You cannot carry any more, your inventory is full", Colors.YELLOW)
            })
        else:
            results.append({
                "item_added": item,
                "message": Message(f"You pick up the {item.name}!", Colors.CYAN)
            })

            self.items.append(item)

        return results

    def use(self, item_entity: Entity, **kwargs) -> List[dict]:
        results = []

        item_component: Item = item_entity.item

        if item_component.use_function is None:
            results.append({"message": Message(f"The {item_entity.name}", Colors.YELLOW)})
        else:
            if item_component.targeting and not (kwargs.get("target_position")):
                results.append({"targeting": item_entity})
            else:
                kwargs = {**item_component.function_kwargs, **kwargs}
                item_use_results = item_component.use_function(self.owner, **kwargs)

                for item_use_result in item_use_results:
                    if item_use_result.get("consumed"):
                        self.remove_item(item_entity)

                results.extend(item_use_results)

        return results

    def remove_item(self, item):
        self.items.remove(item)

    def drop_item(self, item: Entity) -> List[dict]:
        results = []

        item.position: Point = self.owner.position

        self.remove_item(item)
        results.append({"item_dropped": item, "message": Message(f"You dropped the {item.name}", Colors.YELLOW)})

        return results
