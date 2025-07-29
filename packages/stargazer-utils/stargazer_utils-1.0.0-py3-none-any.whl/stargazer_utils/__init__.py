"""
Utility functions without better homes.

Contains iterators, object utility functions, and testing utilities.

Most of these deserve better homes.

### Relevant documentation:
- [CMDline options](https://docs.python.org/3/using/cmdline.html#environment-variables)
- [Developer Mode](https://docs.python.org/3/library/devmode.html#devmode)
- [System Flags (Dev Mode)](https://docs.python.org/3/library/sys.html#sys.flags.dev_mode)

### Legal
SPDX-FileCopyright © 2025 Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

import functools
import operator
import threading
import typing

__all__ = [
    "current_thread_is_main",
    "dump_to_dict",
    "invariant",
]


def current_thread_is_main():
    """
    Returns if the current thread appears to be the main thread.

    That is, returns if the `threading.current_thread` method
    returns the same object as the `threading.main_thread` method,
    which is checked by `is` to check for identity.

    Equilvalent to
    ```
    return (id(threading.current_thread()) == id(threading.main_thread()))
    ```
    """
    # return (id(threading.current_thread()) == id(threading.main_thread()))
    return threading.current_thread() is threading.main_thread()


def dump_to_dict(obj: object, fields: typing.Sequence) -> typing.Dict[str, typing.Any]:
    """
    Helper function that takes an object and creates a dictionary of the specified fields of that object.

    Used like:
    ```python
    class Foo():
        bar = 1
        baz = True

    f_instance = Foo()
    d = dump_to_dict(f_instance, ['bar'])
    d # {'bar': 1}
    ```
    """
    f = operator.attrgetter(*fields)
    return dict(zip(fields, f(obj)))


class InvariantViolation(Exception):
    """
    Never actually catch this. If this is raised then there's a fundamental problem in your
    invariant declaration or your assumptions about the code.

    Fix those!
    """


# returns True so you can write:
# `assert invariant(True)`, and it can be ignored in non-debug code
# Without the assert, invariant will throw a violation in both contexts.
@functools.singledispatch
def invariant(
    obj: object,
    test: typing.Callable[..., bool],
    msg: str | None = None,
) -> bool:
    """
    Declare an invariant in your code.

    Used much like an `assert` statement, but will run even out of `__debug__` contexts.

    ```
    invariant(True)
    invariant(False) # raises
    ```

    If prefaced with `assert`, Python will strip it out of your code out of `__debug__`, which may or may not be what you want.

    If you do preface an `invariant()` call with `assert`, note that the `InvariantViolation` will happen first,
    and you will not see an `AssertionError`.

    Note that typecheckers tend to hate the way that I've defined this. You likely will run into type-checker errors.
    """
    if not test(obj):
        assert callable(test)
        msg = "" if msg is None else msg[:]
        raise InvariantViolation(msg)
    return True


@invariant.register(bool)
def _(condition: bool, msg: str | None = None) -> bool:
    if not condition:
        msg = "" if msg is None else msg[:]
        raise InvariantViolation(msg)
    return True
