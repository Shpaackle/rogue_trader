from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from components.entity_component import EntityComponent

if TYPE_CHECKING:
    from game_messages import Message


class Item(EntityComponent):
    def __init__(self, use_function=None, targeting: bool = False, targeting_message: Optional[Message] = None, **kwargs):
        self.use_function = use_function
        self.targeting: bool = targeting
        self.targeting_message: Optional[Message] = targeting_message
        self.function_kwargs: dict = kwargs
