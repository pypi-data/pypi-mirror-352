"""
Formerly a collection of context managers, but currently only the one.
Most of the former context managers that could have been here are now part of the stdlib.
For example, a long time ago, there was a "AbstractContextManager" definition in this file.

### Legal
SPDX-FileCopyright © 2025 Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

import signal
from contextlib import AbstractContextManager

__all__ = [
    "KeyboardInterruptManager",
]


class KeyboardInterruptManager(AbstractContextManager):
    """
    Used in the main thread to receive a KeyboardInterrupt, but do nothing until the context ends.

    Note that if you're using this, you should probably be running the script through `Click` (or similar) instead, or this should be in your `__name__=="__main__":` handler.

    Due to how signals in python work, this can only be used in the main thread. The original use of this was to allow a handler to properly clean up some download threads.

    Can (and probably should) be subclassed to give the `__exit__` method(s) any additional functionality to clean up resources.
    If you choose to do that, call `super().__exit__(typ, val, tb)` last so that your handler correctly handles the received signal.
    """

    def __init__(self):
        self.signal_received = None
        self._prev_handler = None
        super().__init__()

    def signal_handler(self, received_sig, frame):
        self.signal_received = (received_sig, frame)

    def __enter__(self):
        self.signal_received = None
        self._prev_handler = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, self._prev_handler)
        return self

    def __exit__(self, typ, val, tb):
        signal.signal(signal.SIGINT, self._prev_handler)
        if self.signal_received:
            self._prev_handler(*self.signal_received)  # type: ignore
