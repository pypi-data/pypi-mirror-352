"""
Contains the `Timer` class, which can be used to measure time to roughly 3 decimal digits of precision.
```python
t = Timer()
with t:
    time.sleep(1)
# t.duration available here.
```
Note that this is **not good enough** to do any serious performance testing. It *will* give you a good idea of the timing in file manipulation.

Timer also contains some utility methods for timestamps.
- Timer.utcnow() -> datetime:
- Timer.get_utc() -> int:
- Timer.get_utc_string() -> str:

### Legal
SPDX-FileCopyright © 2025 Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

import time
from contextlib import AbstractContextManager
from datetime import datetime, timedelta, timezone

__all__ = [
    "Timer",
]


class TimerError(RuntimeError):
    """
    Raised on inappropriate usage of the Timer class, *but only in __debug__ contexts*.

    The intent is to help you catch bugs in your code before it's live, not after.

    *Do not catch this Exception type!*

    Contexts where this is raised include but is not necessarily limited to:
    - Stopping a timer that hasn't been started
    - Starting a timer that has already been started but not stopped.
    """


class Timer(AbstractContextManager):
    """
    Timer object used for timing things where extremely high resolution time data doesn't matter.

    If you need sub-millisecond resolution, **this is not an appropriate class**.

    ### As object
    Timer can be used as an object, e.g.:
    ```python
    t = Timer()
    t.start()
    # Some code
    t.stop() # time now available with t.duration
    ```
    Timer objects can be started as soon as they're made like this:
    ```python
    t = Timer(start_now=True)
    ```

    ### As Context Manager
    Timer can be used as a context manager. This is likely the preferred way to use a Timer.
    ```python
    t = Timer()
    with t:
        pass # something you would want to time.
    # t.duration available here.
    ```
    Note that the t instance ***automatically*** starts when entered and stops when exited.

    ### Timing a series.
    Timer can be used to time a series of timestamps.

    Every call to Timer.lap() on a Timer instance will
    add the current time to it's time stamps.

    Starting a timer will start a lap, and stopping the timer
    will end the current lap.

    To put it another way: `t.start(); t.stop` will
    result in the t object having 1 lap in total saved.
    ```python
    t = Timer(start_now=True)
    t.stop()
    # These two lines are the same total duration.
    t.duration
    t.time_stamps[-1] - t.time_stamps[0]

    t.start()
    t.lap()
    t.lap()
    t.stop()
    t.get_laps() # generates 3 laps.
    ```
    """

    def __init__(self, *, start_now: bool = False):
        self.start_time: datetime | None = None
        self.stop_time: datetime | None = None
        self.time_stamps: list[datetime] = []

        if start_now:
            self.start_time = self.utcnow()
            self.time_stamps.append(self.start_time)

    def reset(self) -> None:
        self.start_time = None
        self.stop_time = None
        self.time_stamps = []

    def start(self) -> None:
        # Have we started?
        if self.start_time is None:
            self.start_time = self.utcnow()
            self.time_stamps.append(self.start_time)
            return

        # Have we started but then also stopped it later?
        # Implicit self.start_time is not None here.
        if self.stop_time is not None:
            self.stop_time = None
            self.time_stamps = []

            self.start_time = self.utcnow()
            self.time_stamps.append(self.start_time)
            return

        if __debug__:
            raise TimerError("Timer.start() called on running Timer instance.")

    def stop(self) -> None:
        if __debug__:
            old = self.stop_time

            # Errors for a timer that was inappropriately stopped.
            if self.start_time is None:
                raise TimerError("Timer.stop() called on Timer instance that was not started")

            if old is not None:
                raise TimerError("Timer.stop() called on Timer instance that was already stopped")

        self.stop_time = self.utcnow()
        self.time_stamps.append(self.stop_time)

    @property
    def duration_as_delta(self) -> timedelta:
        if self.start_time is None:
            raise RuntimeError(".duration_as_delta accessed without a start time.")

        return (
            self.stop_time - self.start_time if self.stop_time else self.utcnow() - self.start_time
        )

    @property
    def duration_in_seconds(self) -> float:
        return self.duration_as_delta.total_seconds()

    duration = duration_in_seconds

    def lap(self) -> None:
        self.time_stamps.append(self.utcnow())
        if __debug__ and not self.start_time:
            raise TimerError("Timer.lap() called before timer instance was started.")

    def get_laps(self):
        if self.lap_count > 1:
            for i in range(self.lap_count - 1):
                yield (self.time_stamps[i], self.time_stamps[i + 1])

    @property
    def lap_count(self) -> int:
        return len(self.time_stamps) - 1

    def lap_times(self):
        for start, end in self.get_laps():
            yield end - start

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, typ, val, tb):
        self.stop()

    @classmethod
    def utcnow(cls) -> datetime:
        return datetime.now(tz=timezone.utc)

    @classmethod
    def get_utc(cls) -> int:
        return int(time.time())

    @classmethod
    def get_utc_string(cls) -> str:
        return str(cls.get_utc())
