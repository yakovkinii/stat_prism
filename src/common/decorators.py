#  Copyright (C) 2023-2026  StatPrism Team
#  Balashevych A. K., Petrova N. V., Yakovkin I. I.
#
#  This file is part of StatPrism.
#
#  StatPrism is free software: you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  StatPrism is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  StatPrism.  If not, see <https://www.gnu.org/licenses/>.

# VALIDATED

import functools
import inspect
import logging
import threading
import time

VERBOSE = 15
logging.addLevelName(VERBOSE, "VERBOSE")

LOGGING_LEVEL = VERBOSE
_state = threading.local()

# Per-level indentation marker for the nested-call log (ASCII only).
_INDENT = ". "


def _get_level() -> int:
    return getattr(_state, "level", 0)


def _set_level(value: int) -> None:
    _state.level = value


def _log_call_start(name: str, level: int, levelno: int, source_file: str, line_number: int) -> None:
    ident = _INDENT * level
    logger = logging.getLogger()
    record = logger.makeRecord(
        logger.name,
        levelno,
        source_file,
        line_number,
        ident + name,
        {},
        None,
        "",
    )
    logger.handle(record)


def _log_call_end(message: str, level: int, source_file: str, line_number: int) -> None:
    ident = _INDENT * level
    logger = logging.getLogger()
    record = logger.makeRecord(
        logger.name,
        LOGGING_LEVEL,
        source_file,
        line_number,
        ident + message,
        {},
        None,
        "",
    )
    logger.handle(record)


def log_method(method):
    # Resolve the source location once at decoration time: inspect.getsourcelines re-tokenizes the
    # whole source file, which is far too expensive to do on every call.
    source_file = inspect.getsourcefile(method)
    line_number = inspect.getsourcelines(method)[1]

    @functools.wraps(method)
    def decorator(self, *args, **kwargs):
        if not logging.getLogger().isEnabledFor(LOGGING_LEVEL):
            return method(self, *args, **kwargs)
        class_name = self.__class__.__name__

        level = _get_level()
        _log_call_start(f"{class_name}.{method.__name__}", level, LOGGING_LEVEL, source_file, line_number)

        _set_level(level + 1)
        start_time = time.perf_counter()
        try:
            return method(self, *args, **kwargs)
        finally:
            end_time = time.perf_counter()
            _set_level(level)
            _log_call_end(f"{end_time - start_time:.4f}s", level, source_file, line_number)

    return decorator


def log_method_noarg(method):
    # A no-argument method decorator: the wrapper takes only self, so Qt signals that pass a varying
    # number of arguments depending on the connected signature call through cleanly.
    source_file = inspect.getsourcefile(method)
    line_number = inspect.getsourcelines(method)[1]

    @functools.wraps(method)
    def decorator(self):
        if not logging.getLogger().isEnabledFor(LOGGING_LEVEL):
            return method(self)
        class_name = self.__class__.__name__

        level = _get_level()
        _log_call_start(f"{class_name}.{method.__name__}", level, LOGGING_LEVEL, source_file, line_number)

        _set_level(level + 1)
        start_time = time.perf_counter()
        try:
            return method(self)
        finally:
            end_time = time.perf_counter()
            _set_level(level)
            _log_call_end(f"{end_time - start_time:.4f}s", level, source_file, line_number)

    return decorator


def log_method_experimental(method):  # pragma: no cover
    source_file = inspect.getsourcefile(method)
    line_number = inspect.getsourcelines(method)[1]

    @functools.wraps(method)
    def decorator(self, *args, **kwargs):
        class_name = self.__class__.__name__

        level = _get_level()
        _log_call_start(
            f"{class_name}.{method.__name__} (experimental feature, use with caution!)",
            level,
            logging.WARNING,
            source_file,
            line_number,
        )

        _set_level(level + 1)
        start_time = time.perf_counter()
        try:
            return method(self, *args, **kwargs)
        finally:
            end_time = time.perf_counter()
            _set_level(level)
            _log_call_end(f"{end_time - start_time:.4f}s", level, source_file, line_number)

    return decorator


def log_function(function):
    # Resolve the source location once at decoration time (see log_method).
    source_file = inspect.getsourcefile(function)
    line_number = inspect.getsourcelines(function)[1]

    @functools.wraps(function)
    def decorator(*args, **kwargs):
        if not logging.getLogger().isEnabledFor(LOGGING_LEVEL):
            return function(*args, **kwargs)

        level = _get_level()
        _log_call_start(function.__name__, level, LOGGING_LEVEL, source_file, line_number)

        _set_level(level + 1)
        start_time = time.perf_counter()
        try:
            return function(*args, **kwargs)
        finally:
            end_time = time.perf_counter()
            _set_level(level)
            _log_call_end(
                f"{function.__name__} finished in {end_time - start_time:.6f}s",
                level,
                source_file,
                line_number,
            )

    return decorator


def log_function_experimental(function):  # pragma: no cover
    source_file = inspect.getsourcefile(function)
    line_number = inspect.getsourcelines(function)[1]

    @functools.wraps(function)
    def decorator(*args, **kwargs):
        level = _get_level()
        _log_call_start(
            f"{function.__name__} (experimental feature, use with caution!)",
            level,
            logging.WARNING,
            source_file,
            line_number,
        )

        _set_level(level + 1)
        start_time = time.perf_counter()
        try:
            return function(*args, **kwargs)
        finally:
            end_time = time.perf_counter()
            _set_level(level)
            _log_call_end(
                f"{function.__name__} finished in {end_time - start_time:.6f}s",
                level,
                source_file,
                line_number,
            )

    return decorator
