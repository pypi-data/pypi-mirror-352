from __future__ import annotations

import inspect
from io import StringIO
from typing import TYPE_CHECKING, Any, Dict, Generator, Iterable, List, Optional, Set, TextIO, Type

from ascson.ascsontypes._base import BaseAscsonType
from ascson.typecodes import ETypeCode

if TYPE_CHECKING:
    from ascson.encoder import AscsonEncoder

__all__ = ["AscsonObjectEncoder", "AscsonObject", "AsonAnonymousObject"]


class AscsonObjectEncoder(BaseAscsonType):
    DDID_VERSION: int = 0

    def __init__(self, enc: AscsonEncoder) -> None:
        super().__init__(enc)
        self.TYPE2ID: Dict[AscsonObjectDataDictionary, str] = {}
        self.ID2TYPE: Dict[str, AscsonObjectDataDictionary] = {}
        self.ALL_TYPES: List[AscsonObjectDataDictionary] = []

    def reset(self) -> None:
        self.TYPE2ID.clear()
        self.ID2TYPE.clear()
        self.ALL_TYPES.clear()

    def registerDataDictionary(self, add: AscsonObjectDataDictionary) -> None:
        if add.id in self.ID2TYPE.keys():
            add.ddid = self.ID2TYPE[add.id]
        else:
            add.ddid = len(self.ALL_TYPES)
            self.ALL_TYPES.append(add)
            self.ID2TYPE[add.id] = add
            self.TYPE2ID[add] = add.id

    def getDataDictionaryFor(
        self, data: AscsonObject
    ) -> Optional[AscsonObjectDataDictionary]:
        return self.ID2TYPE.get(data.getAsonTypeID())

    def getOrCreateDataDictionaryFor(
        self, data: AscsonObject
    ) -> Optional[AscsonObjectDataDictionary]:
        atid = data.getAsonTypeID()
        if atid not in self.ID2TYPE.keys():
            self.registerDataDictionary(AscsonObjectDataDictionary.BuildFromObject(data))
        return self.ID2TYPE.get(data.getAsonTypeID())

    def getDataDictionaryByDDID(self, ddid: int) -> Optional[AscsonObjectDataDictionary]:
        return self.ALL_TYPES[ddid]

    def encode(self, data: AscsonObject) -> str:
        add = self.getDataDictionaryFor(data)
        o: str = ""
        if add is None:
            d = {}
            for f in data.getAsonSerializableFields():
                d[f.name] = getattr(data, f.name)
            o += self.encoder.encodeNone()  # No ADD
            o += self.encoder.encodeString(data.getAsonTypeID())
            o += self.encoder.encodeDict(d)
        else:
            o += self.encoder.encodeInteger(add.ddid)
            o += add.encodeBody(data)
        return o

    def decode(self, data: list) -> List[Any]:
        with StringIO(data) as f:
            return self.decodeStream(f)

    def encodeStream(self, f: TextIO, value: AscsonObject) -> None:
        add = self.getDataDictionaryFor(value)
        o: str = ""
        if add is None:
            d = {}
            for f in value.getAsonSerializableFields():
                d[f.name] = getattr(value, f.name)
            o += self.encoder.encodeNone()  # No ADD
            o += self.encoder.encodeString(data.getAsonTypeID())
            o += self.encoder.encodeDict(d)
        else:
            o += self.encoder.encodeInteger(add.ddid)
            o += add.encodeBodyStream(value)
        return o

    def decodeStream(self, f: TextIO) -> List[Any]:
        ddid: Optional[int]
        if (ddid := self.encoder.read()) is None:
            o = AsonAnonymousObject()
            o.typeID = self.encoder.readString()
            for k, v in self.encoder.readDict():
                assert k not in ("typeID",)
                setattr(o, k, v)
            return o
        else:
            add = self.ALL_TYPES[ddid]
            o = add.type()
            data = {}
            allowedFields: Set[str] = set(
                [fld.name for fld in o.getAsonSerializableFields()]
            )
            for fld in add.fields:
                if fld.name not in allowedFields:
                    continue
                data[fld.name] = f.read()
            o.deserializeAsonData(data)
            return o

    def writeDataDictionary(self, f: TextIO) -> None:
        f.write(self.encoder.int.encode(len(self.ALL_TYPES)))
        for i, dde in enumerate(self.ALL_TYPES):
            dde.writeToDataDictionary(self.encoder, i, f)

    def readDataDictionary(self, f: TextIO) -> None:
        dde = None
        for i in range(self.encoder.readInteger(f, skip_id=True)):
            dde = AscsonObjectDataDictionary()
            dde.readDataDictionary(self.encoder, i, f)
        return self


class AsonObjectFieldAssociation:
    def __init__(self) -> None:
        self.ddfid: int = 0
        self.name: str = ""
        self.type: ETypeCode = ETypeCode.NONE

    # def encodeToDataDictionary(self, encoder: AsonEncoder) -> str:
    #     o = encoder.encodeString(self.name)
    #     o += encoder.encodeTypeID(self.type)
    #     return o
    def writeToDataDictionary(self, encoder: AscsonEncoder, f: TextIO) -> None:
        f.write(encoder.str.encode(self.name))
        encoder.writeTypeID(self.type, f)

    def readFromDataDictionary(self, encoder: AscsonEncoder, f: TextIO, i: int) -> None:
        self.ddfid = i
        self.name = encoder.readString(f, skip_id=True)
        self.type = encoder.readTypeID(f)


class AscsonObjectDataDictionary:
    def __init__(self) -> None:
        self.id: str = ""
        self.ddid: int = 0
        self.type: Optional[Type[AscsonObject]] = None
        self.fields: List[AsonObjectFieldAssociation] = []

    def encodeToDataDictionary(self, encoder: AscsonEncoder) -> str:
        o = encoder.str.encode(self.id)
        o += encoder.int.encode(len(self.fields))
        for fld in self.fields:
            o += fld.encodeToDataDictionary(encoder)
        return o

    def writeToDataDictionary(self, encoder: AscsonEncoder, f: TextIO) -> None:
        f.write(encoder.str.encode(self.id))
        f.write(encoder.int.encode(len(self.fields)))
        for fld in self.fields:
            fld.writeToDataDictionary(encoder, f)

    def readDataDictionary(self, encoder: AscsonEncoder, i: int, f: TextIO) -> None:
        self.id = encoder.readString(f, skip_id=True)
        self.ddid = i
        for ddfid in range(encoder.readInteger(f, skip_id=True)):
            fld = AsonObjectFieldAssociation()
            fld.readFromDataDictionary(encoder, fld, ddfid)
            self.fields.append(fld)

    def encodeBodyStream(
        self, encoder: AscsonEncoder, f: TextIO, value: AscsonObject
    ) -> None:
        encoder.writeInteger(self.ddid, f)
        encoder.registerObjectType(value.__class__)
        dd = AscsonObjectDataDictionary.BuildFromObject(value)
        value.serializeToAsonStream(dd, f)

    def encodeBody(self, encoder: AscsonEncoder, value: AscsonObject) -> str:
        encoder.registerObjectType(value.__class__)
        with StringIO() as f:
            encoder.writeInteger(self.ddid, f)
            dd = AscsonObjectDataDictionary.BuildFromObject(value)
            data = value.serializeToAsonStream(dd)
            for aofa in dd.fields:
                encoder.write(data.get(aofa.name))
            return f.getvalue()

    @classmethod
    def BuildFromObject(self, obj: AscsonObject) -> AscsonObjectDataDictionary:
        ddt = AscsonObjectDataDictionary()
        ddt.id = obj.getAsonTypeID()
        ddt.type = type(obj)
        ddt.fields = obj.getAsonSerializableFields()
        return ddt


class AscsonObject:
    ASON_TYPE_ID: Optional[str] = None
    ASON_SERIALIZABLE_FIELDS: Optional[List[str]] = None

    def __init__(self) -> None:
        pass

    @classmethod
    def getAsonTypeID(self) -> str:
        if self.ASON_TYPE_ID is not None:
            return self.ASON_TYPE_ID
        cls = self.__class__
        mod = cls.__module__
        if mod == "builtins":
            return cls.__qualname__
        return f"{mod}.{cls.__qualname__}"
    
    def _getAllFieldNames(self) -> Iterable[str]:
        if self.ASON_SERIALIZABLE_FIELDS is not None:
            for f in sorted(self.ASON_SERIALIZABLE_FIELDS):
                yield f
        else:
            for fld in inspect.getmembers(self, predicate=lambda x: not callable(getattr(self,x[0])) and not x[0].startswith('_')):
                yield fld[0]
        return

    def getAsonSerializableFields(self) -> List[AsonObjectFieldAssociation]:
        o = []
        for fld in self._getAllFieldNames():
            if fld[0].startswith("_"):  # private or protected
                continue
            fa = AsonObjectFieldAssociation()
            fa.name = fld[0]
            fa.type = ETypeCode.NONE
            o.append(fa)
        return o

    def deserializeAsonData(self, data: Dict[str, Any]) -> None:
        for k, v in data.items():
            setattr(self, k, v)

    def serializeToAsonStream(self, dd: AscsonObjectDataDictionary) -> Dict[str, Any]:
        o: Dict[str, Any] = {}
        for field in dd.fields:
            o[field.name] = getattr(self, field.name, None)
        return o


class AsonAnonymousObject:
    def __init__(self) -> None:
        self.typeID: str = ""
