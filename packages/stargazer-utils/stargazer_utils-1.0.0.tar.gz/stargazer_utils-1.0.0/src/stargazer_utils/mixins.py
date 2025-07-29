"""
Short collection of Mixins. These provide some niche functionality, but I also routinely find them useful.


### Legal
SPDX-FileCopyright © 2025 Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

import abc
from json import loads
from operator import attrgetter
from typing import Any

__all__ = [
    "FromJsonMixin",
    "ToJsonMixin",
    "JsonIOMixin",
    "DecimalCounterMixin",
    "HexCounterMixin",
]


class FromJsonMixin(object):
    """
    A Mixin that provides a `from_mapping` and a `from_json_mapping` method.

    `from_mapping` returns an instance of the class when passed a mapping of string:Any

    `from_json_mapping` is the same, but expects that the mapping is still in a JSON str instead.
    """

    @classmethod
    def from_mapping(cls, data: dict[str, Any]):
        return cls(**data)

    @classmethod
    def from_json_mapping(cls, data: str):

        return cls(**loads(data))


class ToJsonMixin(object):
    """
    A Mixin that provides the `to_json` method, which returns a dictionary of fields to values.

    For support, the class inheriting from this must implement the `_serialized_fields` static method,
    which should return a tuple of field names that will be used in the `to_json` method as keys.
    """

    @staticmethod
    def _serialized_fields():
        raise NotImplementedError

    def to_json(self):
        fields = self._serialized_fields()
        getter = attrgetter(*fields)
        return dict(zip(fields, getter(self)))


class JsonIOMixin(FromJsonMixin, ToJsonMixin):
    """
    Literally just `FromJsonMixin` and `ToJsonMixin`, together, for convenience.

    Note that you must still override the "_serialized_fields" static method,
    """

    @staticmethod
    def _serialized_fields():
        raise NotImplementedError


class _BaseCounterMixin(abc.ABC):
    @property
    @abc.abstractmethod
    def counter(self):
        raise NotImplementedError


class DecimalCounterMixin(_BaseCounterMixin):
    def __init__(self):
        self._counter = (1, 2)

    @property
    def counter(self):
        a, b = self._counter
        self._counter = b, a + b
        return a % 1000


class HexCounterMixin(_BaseCounterMixin):
    def __init__(self):
        self._counter = (1, 2)

    @property
    def counter(self):
        a, b = self._counter
        self._counter = b, a + b
        return a % 0xFFFF
