"""
Integers are encoded as 4-bit shorts with an extra bit telling us whether to continue reading numbers.
1 0001
C DATA
"""
from typing import Any, TextIO

from ascson.ascsontypes._base import BaseAscsonType


class AscsonBool(BaseAscsonType):
    def encode(self, data: Any) -> str:
        return "t" if bool(data) else "f"

    def decode(self, data: str) -> bool:
        match data[0]:
            case "t":
                return True
            case "f":
                return False
        return False
    
    def encodeStream(self, f: TextIO, value: Any) -> None:
        return super().encodeStream(f, value)

    def decodeStream(self, f: TextIO) -> bool:
        return self.decode(f.read(1))
