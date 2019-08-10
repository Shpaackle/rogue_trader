from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import item_functions
from components.entity_component import EntityComponent
from game_messages import Message

if TYPE_CHECKING:
    from game_messages import Message


class Item(EntityComponent):
    def __init__(
        self,
        use_function=None,
        targeting: bool = False,
        targeting_message: Optional[Message] = None,
        **kwargs
    ):
        self.use_function = use_function
        self.targeting: bool = targeting
        self.targeting_message: Optional[Message] = targeting_message
        self.function_kwargs: dict = kwargs

    @classmethod
    def from_json(cls, json_data) -> Item:
        use_function_name = json_data.get("use_function_name")
        targeting = json_data.get("targeting")
        targeting_message_data = json_data.get("targeting_message")
        function_kwargs = json_data.get("function_kwargs", {})

        if use_function_name:
            use_function = getattr(item_functions, use_function_name)
        else:
            use_function = None

        if targeting_message_data:
            targeting_message = Message.from_json(targeting_message_data)
        else:
            targeting_message = None

        item = cls(
            use_function=use_function,
            targeting=targeting,
            targeting_message=targeting_message,
            **function_kwargs
        )

        return item

    def to_json(self) -> dict:
        if self.targeting_message:
            targeting_message = (
                self.targeting_message.text,
                self.targeting_message.color.name,
            )
        else:
            targeting_message = None
        json_data = {
            "use_function_name": self.use_function.__name__,
            "targeting": self.targeting,
            "targeting_message": targeting_message,
            "function_kwargs": self.function_kwargs,
        }

        return json_data
