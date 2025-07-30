import struct
from typing import Any, TextIO

from ascson.ascsontypes._base import BaseAscsonType


class AscsonFloat(BaseAscsonType):
    def encode(self, value: float) -> str:
        return self.encoder.int.encode(int.from_bytes(struct.pack("<d", value), "big"))

    def decode(self, data: str) -> float:
        return struct.unpack(
            "<d", int.to_bytes(self.encoder.int.decode(data), 8, byteorder="big")
        )[0]

    def encodeStream(self, f: TextIO, value: Any) -> None:
        return super().encodeStream(f, value)

    def decodeStream(self, f: TextIO) -> float:
        return struct.unpack(
            "<d", int.to_bytes(self.encoder.int.decodeStream(f), 8, byteorder="big")
        )[0]
