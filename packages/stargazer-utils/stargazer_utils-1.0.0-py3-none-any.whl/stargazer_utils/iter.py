"""
A short collection of iterator helpers.

I take no credit for the ones that are explicitly credited to the [itertools recipes](https://docs.python.org/3/library/itertools.html#itertools-recipes).
At time of writing:
- batched
- flatten
- windowed

### Legal
SPDX-FileCopyright © 2025 Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

import functools
import typing
from collections import deque
from itertools import islice, repeat

__all__ = [
    "dilter",
    "first",
    "last",
    "batched",
    "flatten",
    "windowed",
]

dilter: typing.Callable = functools.partial(filter, None)
"""
Default fILTER

Works as `filter(None, iter)`.

That's it.
"""

_sentinel = object()
"""
Default object for certain iter functions within this module.

Raises exceptions when seen.
"""


def first(iterable, default=_sentinel):
    """
    Return the first index of an iterable that supports indexing.
    If indexing is supported, but the iterable is empty, returns the default.
    If the default is not specified, raises the index error.
    e.g.:
    ```
    lst = [1,2,3,4]
    first(lst, None) # 1
    first([], None) # None
    first([]) # Raises
    ```
    """
    try:
        return iterable[0]
    except IndexError:
        if default is _sentinel:
            raise

    return default


def last(iterable, default=_sentinel):
    """
    Return the last index of an iterable that supports indexing.
    If indexing is supported, but the iterable is empty, returns the default.
    If the default is not specified, raises the index error.
    e.g.:
    ```
    lst = [1,2,3,4]
    last(lst, None) # 4
    last([], None) # None
    last([]) # Raises
    ```
    """
    try:
        return iterable[-1]
    except IndexError:
        if default is _sentinel:
            raise

    return default


def batched(iterable, n, *, strict=False):
    """
    `batched` was introduced in Python 3.12,
    with the strict keyword introduced in 3.13
    If the 3.12+ ver is available, you should probably prefer that.
    That said, this version will work in all versions of python 3 where `itertools.islice` is available.

    ```python
    data = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    list(batched(data, 2))
    # [(0, 1), (2, 3), (4, 5), (6, 7), (8,)]
    ```
    """

    if n < 1:
        raise ValueError("n must be at least one")
    iterator = iter(iterable)
    while batch := tuple(islice(iterator, n)):
        if strict and len(batch) != n:
            raise ValueError("batched(): incomplete batch")
        yield batch


def flatten(iterable):
    """
    Based on [moreitertools.collapse](https://more-itertools.readthedocs.io/en/stable/_modules/more_itertools/more.html#collapse)

    Flattens nested iterables to a single iterable. Sometimes called `hard_flatten`.

        >>> list(flatten([[1,2,3], [4,5,6]]))
        [1,2,3,4,5,6]

    Differences from moreitertools.collapse:

    This version ***removes***, and does ***not*** support:
    - The usage of a deque. The import and usage seemed unnecessary, since the original recipe always pops and appends to the left side.
    - The ability to specifiy types that shouldn't be flattened. The only types that avoid being flattened in this one are `str` and `bytes`, and this is explicitly because those types being flattened is actively harmful in almost all cases.
    - The notion of flattening to a specific level of flatness. I consider this a weird usecase and I don't want to support it. Don't be weird: Just flatten your iterables all the way down.
    """

    stack = []
    # Add our first node group, treat the iterable as a single node
    # Needs to be a repeat for later.
    stack.append(repeat(iterable, 1))

    while stack:
        node_group = stack.pop()
        nodes = node_group

        for node in nodes:
            if isinstance(node, (str, bytes, bytearray)):
                yield node
            else:
                try:
                    # try to create child nodes
                    tree = iter(node)
                except TypeError:
                    yield node
                else:
                    # Save current location.
                    # This works because we consumed the iterable up to this point,
                    # and therefore append a partially consumed iterable.
                    stack.append(node_group)
                    # Append the new child node
                    stack.append(tree)
                    # Break to process child node
                    break


def windowed(seq, n):
    """
    Taken from [itertools recipes](https://docs.python.org/3/library/itertools.html#itertools-recipes)

    Collect data into overlapping fixed-length chunks or blocks.

    ```python
    >>> for w in windowed('ABCDEFG', 4):
    >>>    print(w)
    ABCD
    BCDE
    CDEF
    DEFG
    ```
    """

    iterator = iter(seq)
    window = deque(islice(iterator, n - 1), maxlen=n)
    for x in iterator:
        window.append(x)
        yield tuple(window)
