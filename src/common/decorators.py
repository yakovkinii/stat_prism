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


import inspect
import logging

level = 0


def _source_location(callable_):
    source_file = inspect.getsourcefile(callable_) or inspect.getfile(callable_)
    try:
        line_number = inspect.getsourcelines(callable_)[1]
    except (OSError, TypeError):
        code = getattr(callable_, "__code__", None)
        line_number = code.co_firstlineno if code is not None else 0
    return source_file, line_number


def _log_call(callable_, label):
    logger = logging.getLogger()
    source_file, line_number = _source_location(callable_)
    lr = logger.makeRecord(
        logger.name,
        logging.INFO,
        source_file,
        line_number,
        label,
        {},
        None,
        "",
    )
    logger.handle(lr)


def log_method(method):
    """
    A decorator to log the name of a class method when it is executed.
    """

    def decorator(self, *args, **kwargs):
        global level
        class_name = self.__class__.__name__
        ident = "⋅ " * level

        _log_call(method, ident + f"{class_name}.{method.__name__}")

        level += 1
        if args or kwargs:
            result = method(self, *args, **kwargs)
        else:
            result = method(self)
        level -= 1
        return result

    return decorator


def log_method_noarg(method):
    """
    A decorator to log the name of a class method when it is executed.
    Signature is without extra arguments is enforced.
    To use when Qt passes different number of arguments depending on signature.
    """

    def decorator(self):
        global level
        class_name = self.__class__.__name__
        ident = "⋅ " * level

        _log_call(method, ident + f"{class_name}.{method.__name__}")

        level += 1
        result = method(self)
        level -= 1
        return result

    return decorator


def log_function(function):
    """
    A decorator to log the name of a function when it is executed.
    """

    def decorator(*args, **kwargs):
        global level
        ident = "⋅ " * level

        _log_call(function, ident + f"{function.__name__}")

        level += 1
        result = function(*args, **kwargs)
        level -= 1
        return result

    return decorator
