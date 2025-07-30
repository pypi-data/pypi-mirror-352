from enum import Enum


class ETypeCode(Enum):
    INT = "i", "INT"
    BOOL_TRUE = "t", "BOOL_TRUE"
    BOOL_FALSE = "f", "BOOL_FALSE"
    FLOAT = "F", "FLOAT"
    STR_REF = "s", "STR_REF"
    STR_CONST = "S", "STR_CONST"
    LIST = "l", "LIST"
    DICT = "d", "DICT"
    OBJECT = "o", "OBJECT"
    NONE = "n", "NONE"

    INTERNAL_DATA_DICTIONARY = "D", "DATA_DICTIONARY"

    def __init__(self, id: str, key: str) -> None:
        super().__init__()
        self.id = id
        self.key = key
