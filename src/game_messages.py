from __future__ import annotations

import textwrap
from dataclasses import dataclass
from typing import Dict, List

from colors import Colors


@dataclass(init=True, frozen=True)
class Message:

    text: str
    color: Colors = Colors.WHITE

    def __iter__(self):
        return self.text, self.color

    @classmethod
    def from_json(cls, message_json_data) -> Message:
        text = message_json_data[0]
        color = message_json_data[1]
        message = cls(text=text, color=Colors[color])

        return message


class MessageLog:
    def __init__(self, x: int, width: int, height: int):
        self.messages: List[Message] = []
        self.x: int = x
        self.width: int = width
        self.height: int = height

    def add_message(self, message: Message):
        # Split the message if necessary, among multiple lines
        new_msg_lines = textwrap.wrap(message.text, self.width)

        for line in new_msg_lines:
            # If the buffer is full, remove the first line to make room for the new one
            if len(self.messages) == self.height:
                del self.messages[0]

            # Add the new line as a Message object, with the text and the color
            self.messages.append(Message(line, message.color))

    def to_json(self) -> dict:
        messages = []
        for message in self.messages:
            messages.append((message.text, message.color.name))

        json_data = {
            "messages": messages,
            "x": self.x,
            "width": self.width,
            "height": self.height
        }

        return json_data

    @classmethod
    def from_json(cls, json_data):
        x = json_data["x"]
        width = json_data["width"]
        height = json_data["height"]
        message_log = cls(x=x, width=width, height=height)

        messages_json_data = json_data["messages"]

        for message_json_data in messages_json_data:
            text, color = message_json_data
            message = Message(text=text, color=Colors[color])
            message_log.add_message(message)

        return message_log


