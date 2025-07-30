"""
Integers are encoded as 4-bit shorts with an extra bit telling us whether to continue reading numbers.
"""
import string
from typing import Any, TextIO

from ascson.ascsontypes._base import BaseAscsonType

ALPHABET: str = (string.digits + string.ascii_uppercase)[:32]

MAXVAL = 0b10000
ALL_MASK = 0x1F
ALL_BITS_PER_CHUNK = 5
USABLE_MASK = 0b1111
USABLE_BITS_PER_CHUNK = 4
FLAG_CONTINUE = 0b10000


class AscsonInteger(BaseAscsonType):
    def encode(self, value: int) -> str:
        o = ""
        if value == 0:
            return "0"
        if value < 0:
            o += "-"
            value = abs(value)
        while value >= MAXVAL:
            o += ALPHABET[(value & USABLE_MASK) | FLAG_CONTINUE]
            value >>= 4
        return o + ALPHABET[(value)]

    def decode(self, data: str) -> int:
        o = 0
        negative = False
        if data.startswith("-"):
            data = data[1:]
            negative = True
        shf = 0
        for i, c in enumerate(data):
            v = ALPHABET.index(c)
            o |= (v & USABLE_MASK) << shf
            shf += 4
            if (v & FLAG_CONTINUE) != FLAG_CONTINUE:
                if negative:
                    return 1 - o
                return o
        raise Exception("Bad 5-bit integer (ran out of bits)")
    
    def encodeStream(self, f: TextIO, value: int) -> None:
        if value == 0:
            f.write('0')
            return
        if value < 0:
            f.write("-")
            value = abs(value)
        while value >= MAXVAL:
            f.write(ALPHABET[(value & USABLE_MASK) | FLAG_CONTINUE])
            value >>= 4
        f.write(ALPHABET[(value)])

    def decodeStream(self, f: TextIO) -> int:
        o = 0
        negative = False
        shf = 0
        for i in range(50):
            c = f.read(1)
            if i == 0 and c == "-":
                negative = True
                continue
            v = ALPHABET.index(c)
            o |= (v & USABLE_MASK) << shf
            shf += 4
            if not v & FLAG_CONTINUE:
                if negative:
                    o = 1 - o
                return o
        raise Exception("Bad 5-bit integer (ran out of bits)")
