from io import StringIO
from typing import Any, Iterable, List, TextIO

from ascson.ascsontypes._base import BaseAscsonType


class AscsonList(BaseAscsonType):
    def encode(self, data: Iterable[Any]) -> str:
        o = self.encoder.int.encode(len(data))
        for v in data:
            o += self.encoder.encode(v)
        return o

    def decode(self, data: list) -> List[Any]:
        with StringIO(data) as f:
            return self.decodeStream(f)
        
    def encodeStream(self, f: TextIO, value: Any) -> None:
        self.encoder.int.encodeStream(f,len(value))
        for e in value:
            self.encoder.encodeStream(e)

    def decodeStream(self, f: TextIO) -> List[Any]:
        l = self.encoder.int.decodeStream(f)
        o = []
        for _ in range(l):
            v = self.encoder.read(f)
            assert v is not None
            o.append(v)
        return o
