import collections
from io import StringIO
from typing import Any, TextIO

from ascson.ascsontypes._base import BaseAscsonType


class AscsonDict(BaseAscsonType):
    def encode(self, data: dict) -> str:
        o = self.encoder.int.encode(len(data))
        for k, v in data.items():
            o += self.encoder.encode(k)
            o += self.encoder.encode(v)
        return o

    def decode(self, data: dict) -> str:
        with StringIO(data) as f:
            return self.decodeStream(f)
    
    def encodeStream(self, f: TextIO, value: Any) -> None:
        return super().encodeStream(f, value)

    def decodeStream(self, f: TextIO) -> dict:
        l = self.encoder.int.decodeStream(f)
        o = collections.OrderedDict()
        for _ in range(l):
            k = self.encoder.read(f)
            v = self.encoder.read(f)
            o[k] = v
        return o
