"""
A collection of decorators. Well, just the one right now.

### Legal
SPDX-FileCopyright © 2025 Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

import functools
import random
import time

__all__ = [
    "exponential_retry",
]


def exponential_retry(caught_exceptions=None, max_tries=3, base_delay=2):
    """
    An exponential retry function, intended to consume API ~~or scrape pages~~ where you don't necessarily know the rate limit ahead of time,
    but can be adapted for less surriptitious code as well.

    Uses a slight jitter on the delay for... reasons.
    """

    if caught_exceptions is None:
        caught_exceptions = (Exception,)

    def deco_retry(f):
        @functools.wraps(f)
        def f_retry(*args, **kwargs):
            tries_left = max_tries - 1
            delay = base_delay + random.uniform(0, 1)
            while tries_left > 0:
                try:
                    return f(*args, **kwargs)
                except caught_exceptions:
                    time.sleep(delay)

                    tries_left -= 1
                    expo = max_tries - tries_left
                    delay = (base_delay**expo) + random.uniform(0, 1)

            # Try last time without a catch.
            return f(*args, **kwargs)

        return f_retry

    return deco_retry
