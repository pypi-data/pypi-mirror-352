from io import StringIO
from typing import Any, TextIO

from ascson.ascsontypes.obj import AscsonObjectEncoder
from ascson.encoder import AscsonEncoder


def dumps(input_: Any) -> str:
    with StringIO() as f:
        dump(input_, f)
        return f.getvalue()


def loads(data: str) -> Any:
    with StringIO(data) as f:
        return load(f)


def load(f: TextIO) -> Any:
    e = AscsonEncoder()
    o = e.read(f)
    if not isinstance(o, AscsonObjectEncoder):
        return o
    return e.read(f)


def dump(data: Any, f: TextIO) -> None:
    e = AscsonEncoder()
    e.collectTypesFrom(data)
    e.writeDataDictionary(f, not_if_empty=True)
    e.write(data, f)
