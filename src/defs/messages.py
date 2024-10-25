from typing import Literal, TypedDict


class SimpleMessage(TypedDict):
    role: Literal["user", "assistant"]
    content: str


__all__ = [SimpleMessage]
