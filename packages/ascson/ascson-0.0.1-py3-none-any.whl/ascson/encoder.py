import collections.abc
from typing import Any, Iterable, TextIO, Type

from ascson.ascsontypes._base import BaseAscsonType
from ascson.ascsontypes.bool import AscsonBool
from ascson.ascsontypes.dict import AscsonDict
from ascson.ascsontypes.float import AscsonFloat
from ascson.ascsontypes.int import AscsonInteger
from ascson.ascsontypes.list import AscsonList
from ascson.ascsontypes.obj import (AscsonObject, AscsonObjectDataDictionary,
                                    AscsonObjectEncoder)
from ascson.ascsontypes.str import AscsonString
from ascson.typecodes import ETypeCode


class AscsonEncoder:
    INT_TYPE: Type[BaseAscsonType] = AscsonInteger
    STR_TYPE: Type[BaseAscsonType] = AscsonString
    FLOAT_TYPE: Type[BaseAscsonType] = AscsonFloat
    BOOL_TYPE: Type[BaseAscsonType] = AscsonBool
    DICT_TYPE: Type[BaseAscsonType] = AscsonDict
    LIST_TYPE: Type[BaseAscsonType] = AscsonList
    OBJECT_TYPE: Type[AscsonObjectEncoder] = AscsonObjectEncoder

    def _initType(self, t: Type[BaseAscsonType]) -> BaseAscsonType:
        return t(self)

    def __init__(self) -> None:
        self.int: BaseAscsonType = self._initType(self.INT_TYPE)
        self.str: BaseAscsonType = self._initType(self.STR_TYPE)
        self.float: BaseAscsonType = self._initType(self.FLOAT_TYPE)
        self.bool: BaseAscsonType = self._initType(self.BOOL_TYPE)
        self.dict: BaseAscsonType = self._initType(self.DICT_TYPE)
        self.list: BaseAscsonType = self._initType(self.LIST_TYPE)
        self.object: AscsonObjectEncoder = self._initType(self.OBJECT_TYPE)

    def write(self, value: Any, f: TextIO) -> None:
        if value is None:
            self.writeNone(f)
            return
        match value:
            case bool():
                self.writeBoolean(value, f)
                return
            case float():
                self.writeFloat(value, f)
                return
            case int():
                self.writeInteger(value, f)
                return
            case str():
                self.writeString(value, f)
                return
        if isinstance(value, dict):
            self.writeDict(value, f)
            return
        elif isinstance(value, Iterable):
            self.writeList(value, f)
            return
        elif isinstance(value, AscsonObject):
            self.writeObject(value, f)
            return

    def encode(self, value: Any) -> str:
        if value is None:
            return self.encodeNone()
        match value:
            case bool():
                return self.encodeBoolean(value)
            case float():
                return self.encodeFloat(value)
            case int():
                return self.encodeInteger(value)
            case str():
                return self.encodeString(value)
        if isinstance(value, AscsonObject):
            return self.object.encode(value)
        elif isinstance(value, dict):
            return self.dict.encodeStream(value)
        elif isinstance(value, collections.abc.Iterable):
            return self.list.encodeStream(value)

    def registerObjectType(self, cls: Type[AscsonObject]) -> None:
        i = cls()
        aodd: AscsonObjectDataDictionary = self.object.getOrCreateDataDictionaryFor(i)
        return aodd

    def encodeStream(self, f: TextIO, value: Any) -> str:
        if value is None:
            f.write(self.encodeNone())
        match value:
            case bool():
                self.bool.encodeStream(f, value)
            case float():
                self.float.encodeStream(f, value)
            case int():
                self.int.encodeStream(f, value)
            case str():
                self.str.encodeStream(f, value)
        if isinstance(value, AscsonObject):
            self.object.encodeStream(f, value)
        elif isinstance(value, dict):
            self.dict.encodeStream(f, value)
        elif isinstance(value, collections.abc.Iterable):
            self.list.encodeStream(f, value)

    def collectTypesFrom(self, value: Any) -> None:
        if value is None:
            return
        match value:
            case bool():
                return
            case float():
                return
            case int():
                return
            case str():
                return
        if isinstance(value, dict):
            self.collectDict(value)
        elif isinstance(value, collections.abc.Iterable):
            self.collectList(value)
        elif isinstance(value, AscsonObject):
            self.registerObjectType(type(value))

    def read(self, f: TextIO) -> Any:
        t = f.read(1)
        match t:
            case ETypeCode.BOOL_TRUE.id:
                return True
            case ETypeCode.BOOL_FALSE.id:
                return False
            case ETypeCode.FLOAT.id:
                return self.float.decodeStream(f)
            case ETypeCode.INT.id:
                return self.int.decodeStream(f)
            case ETypeCode.STR_CONST.id:
                return self.str.decodeStream(f)
            case ETypeCode.DICT.id:
                return self.dict.decodeStream(f)
            case ETypeCode.LIST.id:
                return self.list.decodeStream(f)
            case ETypeCode.OBJECT.id:
                return self.object.decodeStream(f)
            case ETypeCode.NONE.id:
                return None
            case ETypeCode.INTERNAL_DATA_DICTIONARY.id:
                return self.object.readDataDictionary(f)
            case _:
                raise Exception(f"Unknown type prefix {t!r}")

    def decode(self, value: str) -> Any:
        t = value[0]
        d = value[1:] if len(value) > 1 else ""
        match t:
            case ETypeCode.BOOL_TRUE.id:
                return True
            case ETypeCode.BOOL_FALSE.id:
                return False
            case ETypeCode.FLOAT.id:
                return self.float.decode(d)
            case ETypeCode.INT.id:
                return self.int.decode(d)
            case ETypeCode.STR_CONST.id:
                return self.str.decode(d)
            case ETypeCode.DICT.id:
                return self.dict.decode(d)
            case ETypeCode.LIST.id:
                return self.list.decode(d)
            case ETypeCode.OBJECT.id:
                return self.object.decode(d)
            case ETypeCode.NONE.id:
                return None
            case ETypeCode.INTERNAL_DATA_DICTIONARY.id:
                raise NotImplemented()
            case _:
                raise Exception(f"Unknown type prefix {t!r}")

    def registerObjectType(self, cls: Type[AscsonObject]) -> None:
        i = cls()
        aodd: AscsonObjectDataDictionary = self.object.getOrCreateDataDictionaryFor(i)
        return aodd

    def encodeNone(self) -> str:
        return ETypeCode.NONE.id

    def writeNone(self, f: TextIO) -> None:
        f.write(ETypeCode.NONE.id)

    def decodeNone(self, s: str, skip_id: bool = False) -> None:
        return None

    def readNone(self, f: TextIO, skip_id: bool = False) -> None:
        if not skip_id:
            f.seek(1)
        return None

    def encodeBoolean(self, value: bool) -> str:
        return self.bool.encode(value)

    def writeBoolean(self, value: bool, f: TextIO) -> None:
        f.write(self.bool.encode(value))

    def decodeBoolean(self, s: str, skip_id: bool = False) -> bool:
        return self.bool.decode(s)

    def readBoolean(self, f: TextIO, skip_id: bool = False) -> bool:
        return self.bool.decodeStream(f)

    def encodeFloat(self, value: float) -> str:
        return ETypeCode.FLOAT.id + self.float.encode(value)

    def writeFloat(self, value: float, f: TextIO) -> None:
        f.write(self.encodeFloat(value))

    def decodeFloat(self, s: str, skip_id: bool = False) -> float:
        return self.float.decode(s)

    def readFloat(self, f: TextIO, skip_id: bool = False) -> float:
        if not skip_id:
            f.seek(1)
        return self.float.decodeStream(f)

    def encodeInteger(self, value: int) -> str:
        return ETypeCode.INT.id + self.int.encode(value)

    def writeInteger(self, value: int, f: TextIO) -> None:
        f.write(ETypeCode.INT.id)
        f.write(self.int.encode(value))

    def decodeInteger(self, s: str, skip_id: bool = False) -> int:
        return self.int.decode(s)

    def readInteger(self, f: TextIO, skip_id: bool = False) -> int:
        if not skip_id:
            f.seek(1)
        return self.int.decodeStream(f)

    def encodeString(self, value: str) -> str:
        return ETypeCode.STR_CONST.id + self.str.encode(value)

    def writeString(self, value: str, f: TextIO) -> None:
        f.write(self.encodeString(value))

    def decodeString(self, s: str, skip_id: bool = False) -> str:
        return self.str.decode(s)

    def readString(self, f: TextIO, skip_id: bool = False) -> str:
        if not skip_id:
            f.seek(1)
        return self.str.decodeStream(f)

    def encodeDict(self, value: dict) -> str:
        return ETypeCode.DICT.id + self.dict.encode(value)

    def collectDict(self, value: dict) -> None:
        for k, v in value.items():
            self.collectTypesFrom(k)
            self.collectTypesFrom(v)

    def writeDict(self, value: dict, f: TextIO) -> None:
        f.write(self.encodeDict(value))

    def decodeDict(self, s: str, skip_id: bool = False) -> dict:
        return self.dict.decode(s)

    def readDict(self, f: TextIO, skip_id: bool = False) -> dict:
        if not skip_id:
            f.seek(1)
        return self.dict.decodeStream(f)

    def encodeList(self, value: Iterable[Any]) -> str:
        return ETypeCode.LIST.id + self.list.encode(value)

    def collectList(self, value: Iterable[Any]) -> None:
        for v in value:
            self.collectTypesFrom(v)

    def writeList(self, value: Iterable[Any], f: TextIO) -> None:
        f.write(self.encodeList(value))

    def decodeList(self, s: str, skip_id: bool = False) -> list:
        return self.list.decode(s)

    def readList(self, f: TextIO, skip_id: bool = False) -> list:
        if not skip_id:
            f.seek(1)
        return self.list.decodeStream(f)

    # def encodeDataDictionary(self) -> str:
    #     return ETypeCode.INTERNAL_DATA_DICTIONARY.id + self.object.encodeDataDictionary()
    def writeDataDictionary(self, f: TextIO, not_if_empty: bool = False) -> None:
        if not_if_empty and len(self.object.ALL_TYPES) == 0:
            return
        f.write(ETypeCode.INTERNAL_DATA_DICTIONARY.id)
        self.object.writeDataDictionary(f)

    def readDataDictionary(self, f: TextIO) -> None:
        self.object.readDataDictionary(f)

    def encodeObject(self, value: AscsonObject) -> str:
        return ETypeCode.OBJECT.id + self.object.encode(value)

    def writeObject(self, value: AscsonObject, f: TextIO) -> None:
        f.write(self.encodeObject(value))

    def decodeObject(self, s: str, skip_id: bool = False) -> AscsonObject:
        return self.object.decode(s)

    def readObject(self, f: TextIO, skip_id: bool = False) -> AscsonObject:
        if not skip_id:
            f.seek(1)
        return self.object.decodeStream(f)

    def readTypeID(self, f: TextIO) -> ETypeCode:
        tid: str = f.read(1)
        for tc in ETypeCode:
            if tc.id == tid:
                return tc
        return None

    def writeTypeID(self, value: ETypeCode, f: TextIO) -> None:
        f.write(value.id)
