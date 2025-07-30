# ASCSON for Python
*ASCII Serialized Object Notation*

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Releases](https://gitlab.com/N3X15/ascson/-/badges/release.svg)](https://gitlab.com/N3X15/ascson/-/releases)

## What?

This is basically a way to write binary data to text files with a structure similar to actual binary files.  Also includes a system for writing formatted data in a way similar to NBT.

## Why?!

I have always wondered what it would look like if binary flatfiles were encoded in a readable way, and if I could come up with something relatively efficient.

This is the result of that question, answered by a very sleep-deprived me on a cold Tuesday night in February 2023. I've since cleaned it up a bit.

## Caveats

If you actually need to store data efficiently but in an ASCII format, I highly suggest looking elsewhere.  Packing data to binary and then dumping to Base64 is probably way better than this burning dumpster fire.

## Installing

`pip install https://gitlab.com/N3X15/ascson.git`

## Usage

### Encoding
```python
import ascson

o: str = ascson.dumps({
    'a': 1,
    'b': 2.5,
    'c': True,
    'd': 'A longer string.'
})

print(o)
```
```
d4S1ai1S1bFGK4S1ctS1dSG1A longer string.
```

### Decoding
```python
import ascson

o = ascson.loads('d4S1ai1S1bFGK4S1ctS1dSG1A longer string.')

print(repr(o))
```
```
OrderedDict([('a', 1), ('b', 2.5), ('c', True), ('d', 'A longer string.')])
```
## How it works

Let's break it up a bit.

```python
# ints are encoded as 4-bit integers with a 5th bit,
# used to tell the parser whether to continue reading characters.
assert ascson.dumps(1) == "i1"
assert ascson.dumps(-1) == "i-1"
assert ascson.dumps(123) == "iR7"
# String constants are prefixed with 'S' and the 4-bit encoded length of the string in characters (NOT bytes).
assert ascson.dumps("") == "S0"
assert ascson.dumps("a") == "S1a"
# Floats are prefixed with 'F', converted to bytes (double-format for accuracy), read as a big-endian integer, encoded as an ascson integer.
assert ascson.dumps(1.5) == "FVJOF"
# True booleans are presented as the letter 't'
assert ascson.dumps(True) == "t"
# False booleans are presented as the letter 'f'
assert ascson.dumps(False) == "f"
# Dictionaries are prefixed with 'd' and the 4-bit encoded length of the dictionary.
# Each key-value pair then follows.
assert ascson.dumps(dict()) == "d0"
assert ascson.dumps(dict(a=2)) == "d1S1ai2"
# Lists are prefixed with 'l' and the 4-bit encoded length of the list
assert ascson.dumps([]) == "l0"
assert ascson.dumps(["a"]) == "l1S1a"
```

## License

As usual, this is available to you under the Terms of the [MIT Open-Source License Agreement](/LICENSE).

## Contributing

Any merge requests or issue reports are welcome.  I have a day job, so this may get updated infrequently.
