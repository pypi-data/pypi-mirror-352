from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, TextIO

if TYPE_CHECKING:
    from ascson.encoder import AscsonEncoder


class BaseAscsonType(ABC):
    def __init__(self, enc: AscsonEncoder) -> None:
        self.encoder: AscsonEncoder = enc

    @abstractmethod
    def encode(self, value: Any) -> str:
        pass

    @abstractmethod
    def decode(self, data: str) -> Any:
        pass

    def encodeStream(self, f: TextIO, value: Any) -> None:
        f.write(self.encode(value))

    @abstractmethod
    def decodeStream(self, f: TextIO) -> Any:
        pass
