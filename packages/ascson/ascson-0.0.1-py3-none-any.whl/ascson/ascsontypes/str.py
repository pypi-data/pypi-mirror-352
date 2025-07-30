from io import StringIO
from typing import TextIO

from ascson.ascsontypes._base import BaseAscsonType


class AscsonString(BaseAscsonType):
    def encode(self, data: str) -> str:
        return self.encoder.int.encode(len(data)) + data

    def decode(self, data: str) -> str:
        with StringIO(data) as f:
            return self.decodeStream(f)

    def decodeStream(self, f: TextIO) -> str:
        l = self.encoder.int.decodeStream(f)
        return f.read(l)
