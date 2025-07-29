"""
### Legal
SPDX-FileCopyright © 2025 Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

__all__ = [
    "UTF_8_ENCODING",
    "OPEN_MODE",
    "OPEN_MODE_BINARY",
    "READ_MODE",
    "READ_MODE_BINARY",
    "WRITE_MODE",
    "WRITE_MODE_BINARY",
    "to_utf8_bytes",
    "read_utf8_data",
    "write_utf8_data",
]


UTF_8_ENCODING = "utf-8"

OPEN_MODE = "rt"
WRITE_MODE = "wt"
OPEN_MODE_BINARY = "rb"
WRITE_MODE_BINARY = "wb"
READ_MODE, READ_MODE_BINARY = OPEN_MODE, OPEN_MODE_BINARY
EXCLUSIVE_MODE = "x"
"""
> `open for exclusive creation, failing if the file already exists`

Use like:
```python
with open(file, mode=WRITE_MODE + EXCLUSIVE_MODE) as f:
    # Do something with a guarenteed new file here.
    ...
...
```
"""


def to_utf8_bytes(to_encode: str):
    """
    Convenience function to encode a string from UTF-8 to bytes.
    """
    return bytes(
        to_encode,
        UTF_8_ENCODING,
    )


def read_utf8_data(file_path: str):
    """
    Opens a byte-encoded file and returns the contents as a UTF-8 decoded string.
    """
    with open(file_path, mode=OPEN_MODE_BINARY) as f:
        return f.read().decode(UTF_8_ENCODING)


def write_utf8_data(file_path: str, data: str):
    """
    Encodes a string to bytes and writes them to a file.
    """
    with open(file_path, WRITE_MODE_BINARY) as f:
        return f.write(data.encode(UTF_8_ENCODING))
