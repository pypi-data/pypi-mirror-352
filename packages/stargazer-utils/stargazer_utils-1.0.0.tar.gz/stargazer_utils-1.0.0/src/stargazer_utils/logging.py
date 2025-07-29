"""
Logging shortcuts.
`get_logger_for` is probably the function you want.
```python
logger = get_logger_for(__file__)
logger.info("Just works!")
```

Inspired in part by [a guy on StackOverflow](https://stackoverflow.com/questions/7016056/python-logging-not-outputting-anything/56144390#56144390) who claimed
> # Your script/app needs to call this somewhere at least once.
> logging.basicConfig()

Turns out, no you don't!

### Legal
SPDX-FileCopyright © 2025 Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

import logging
import os
import sys
import time

__all__ = [
    "get_logger_for",
    "get_short_logger_for",
    "get_debug_logger_for",
]

# https://docs.python.org/3.11/library/logging.html#logrecord-attributes
_default_debug_format = "{name}.{thread:d}.{funcName}.{lineno}.{levelname}-{asctime}:\n\t{message}"
_default_prod_format = "{levelname}-{asctime}:\t{message}"
_default_dt_format = "%Y/%m/%d@%H:%M:%S"


def get_logger_for(
    py_file_name,
    /,
    log_format=None,
    *,
    date_format=None,
    log_to_file=False,
    log_to_stdout=False,
    propogate=False,
    debug_config=__debug__,
):
    """
    Standardized logger. (I got tired of having to format that thing in every file.)

    Generally used like:
    ```python
    logger = get_logger_for(__file__)
    logger.info("Just works!")
    ```
    That's it.

    ### Relevant documentation:
    - [Logging How-To](https://docs.python.org/3/howto/logging.html#logging-advanced-tutorial)
    - [Logging Cookbook](https://docs.python.org/3/howto/logging-cookbook.html)
    - [Logging Tutorial Links](https://docs.python.org/3/howto/logging.html#tutorial-ref-links)
    """

    _default_log_format = (
        _default_debug_format if __debug__ and debug_config else _default_prod_format
    )

    # https://docs.python.org/3/library/time.html#time.strftime
    _dt_format = _default_dt_format if date_format is None else date_format[:]
    _log_format = _default_log_format if log_format is None else log_format[:]

    formatter = logging.Formatter(_log_format, datefmt=_dt_format, style="{")
    logging_level = logging.DEBUG if __debug__ and debug_config else logging.INFO

    # https://docs.python.org/3/library/logging.html#logging.Logger.addHandler
    stdout_stream_handler = logging.StreamHandler(sys.stdout)
    stdout_stream_handler.setLevel(level=logging_level)
    stdout_stream_handler.setFormatter(formatter)

    if log_to_file:
        # Yes, the sgtimer class has this exact functionality
        # but there's no other reason to import the class,
        # So I want to avoid the import to prevent any circular nonsense.
        logfile_handler = logging.FileHandler(f"{py_file_name}.{int(time.time())}.log")
        logfile_handler.setLevel(level=logging_level)
        logfile_handler.setFormatter(formatter)

    # https://docs.python.org/3/library/sys.html?highlight=sys%20stderr#sys.stderr
    if log_to_stdout:
        stderr_stream_handler = logging.StreamHandler(sys.stderr)
        stderr_stream_handler.setLevel(level=logging_level)
        stderr_stream_handler.setFormatter(formatter)

    logger = logging.getLogger(os.path.basename(py_file_name))
    logger.addHandler(stdout_stream_handler)
    if log_to_file:
        logger.addHandler(logfile_handler)
    if log_to_stdout:
        logger.addHandler(stderr_stream_handler)

    logger.setLevel(level=logging_level)
    logger.propagate = propogate

    return logger


def get_short_logger_for(py_file_name):
    """
    Standardized logger that always formats for prod.

    Used like:
    ```python
    logger = get_succinct_logger_for(__file__)
    logger.info("Just works!")
    ```

    That's it.
    """

    return get_logger_for(
        py_file_name,
        log_format=_default_prod_format,
        date_format=_default_dt_format,
        debug_config=False,
    )


def get_debug_logger_for(py_file_name):
    """
    Standardized logger that always formats for debug.

    Used like:
    ```python
    logger = get_debug_logger_for(__file__)
    logger.info("Just works!")
    ```

    That's it.
    """
    return get_logger_for(
        py_file_name,
        log_format=_default_debug_format,
        date_format=_default_dt_format,
        debug_config=True,
    )
