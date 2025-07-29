"""
A short set of JSON helpers. Also exports `dump`, `dumps`, `load` and `loads` from the stdlib json library as a convenience.

### Legal
SPDX-FileCopyright © 2025 Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

import typing
from contextlib import AbstractContextManager
from json import dump, dumps, load, loads

from . import OPEN_MODE, UTF_8_ENCODING, write_utf8_data

__all__ = [
    "dump",
    "dumps",
    "load",
    "loads",
    "JSON_EXT",
    "DOT_JSON",
    "JSONIndentConsts",
    "JSONFileUpdateHandler",
    "read_utf8_json_data",
    "write_utf8_json_data",
    "squish_json",
]

JSON_EXT = "json"
DOT_JSON = ".json"


class JSONIndentConsts(object):
    """
    Short constants to (hopefully) make reading json indentation a little easier.
    """

    STANDARD = 2 if __debug__ else None
    SPARSE = 4
    LOOSE = 2
    TIGHT: None = None


def read_utf8_json_data(file_path: str):
    """
    Opens a file containing JSON data, closes it, and returns the contents as a JSON object.
    """
    with open(file_path, OPEN_MODE, encoding=UTF_8_ENCODING) as json_data:
        return load(json_data)


def write_utf8_json_data(
    file_path: str,
    json_data: typing.Any,  # I cannot be assed to type this correctly.
    indent: int | None = JSONIndentConsts.LOOSE,
    sort_keys=False,
    ensure_ascii=False,
    **kwargs,
):
    """
    Writes valid JSON to a file after converting it to a string representation.
    """
    data = dumps(json_data, indent=indent, sort_keys=sort_keys, ensure_ascii=ensure_ascii, **kwargs)
    return write_utf8_data(file_path, data)


def squish_json(json_data: dict | list, **kwargs) -> str:
    """
    Formats JSON data to the tightest possible representation in str form.
    """
    return dumps(json_data, indent=JSONIndentConsts.TIGHT, separators=(",", ":"), **kwargs)


class JSONFileUpdateHandler(AbstractContextManager):
    """
    When used as a context manager:
    1. Opens, reads and closes a JSON file.
    2. Can receive updates to the .data attribute
    3. Opens, writes, and closes the same JSON file with the contents of .data

    This class will fail (intentionally!) if the file does not exist when the class is instantiated.
    """

    def __init__(self, file_path: str, indentation=JSONIndentConsts.STANDARD):
        self.file_path = file_path
        self.data = read_utf8_json_data(file_path)
        self.indentation = indentation

    def __enter__(self):
        return self

    def __exit__(self, typ, val, tb):
        write_utf8_json_data(self.file_path, self.data, indent=self.indentation)
