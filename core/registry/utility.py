import inspect
import logging

import numpy as np
import pandas as pd

from core.globals.result import result_container
from core.registry.constants import NO_RESULT_SELECTED


def get_html_start_end():
    html_start = """
    <!DOCTYPE html>
    <html lang="en">

    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Your Page Title</title>
        <style>
            /* Base Table Styles */
            tabledata {
                border-collapse: collapse;
                font-size: 18px;
                width: 100%;
                display: block;
                overflow-x: auto;
                white-space: nowrap;
                text-align: right;
            }

            th, td {
                padding: 8px 12px;
                border: 1px solid #ddd;
                width: 50px;
                min-width: 50px;
                position:relative;
            }

            th {
                background-color: #f7f9fa;
            }

            tr:hover {
                background-color: #e5f3f8;
            }

            /* Freeze the first column */
            td:first-child, th:first-child {
                position: sticky;
                left: 0;
                z-index: 1;
                font-weight:800;
                background-color: #f7f9fa;
            }
            .hidden_first_th th:first-child {{
                visibility: hidden;
            }}
        </style>
    </head>

    <body style="background-color: white;">
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center; width:100%;">
        """
    html_end = """
    </div>
    </body>
    </html>
    """
    return html_start, html_end


def smart_comma_join(items):
    if len(items) == 0:
        return ""

    if len(items) == 1:
        return items[0]

    if len(items) == 2:
        return f"{items[0]} and {items[1]}"

    return ", ".join(items[:-1]) + f", and {items[-1]}"


def round_to_significant_digits(num, n=4):
    if num == 0:
        return 0  # Handle the special case where the number is zero
    else:
        return round(num, -int(np.floor(np.log10(abs(num))) - (n - 1)))


def get_next_valid_result_id():
    if result_container.results:
        return max(result_container.results.keys()) + 1
    else:
        return 0


def select_result(result_id: int):
    if result_id == NO_RESULT_SELECTED:
        result_container.current_result = NO_RESULT_SELECTED
        return
    if result_id in result_container.results.keys():
        result_container.current_result = result_id
        return
    raise ValueError(f"Trying to select non-existing result {result_id}")


def num_to_str(num, digits=4):
    default_str = str(num)

    if len(default_str) <= digits:
        return default_str

    if isinstance(num, int):
        return default_str

    # Split the number into whole and decimal parts
    whole, decimal = str(num).split(".") if "." in str(num) else (str(num), None)

    # If the decimal part exists, format it to ensure it's trimmed
    if decimal:
        if len(whole) >= digits:
            return whole

        if num == 0:
            return 0  # just in case

        return str(round(num, -int(np.floor(np.log10(abs(num))) - (digits - 1))))
        # return f"{whole}.{decimal[:digits-len(whole)]}"  # Taking the first three characters of the decimal part
    else:
        return whole


def round_series(series: pd.Series, n=4):
    return series.apply(round_to_significant_digits, args=(n,))


def div_title():
    return (
        "<div style=\"font-size:32px;text-align:center; font-family: 'Open Sans'; color:#000077;"
        + 'font-weight: 500;margin:20px;">'
    )


def div_text():
    return (
        "<div style=\"font-size:24px;text-align:justify; font-family: 'Open Sans'; color:#000077;"
        + 'font-weight: 500;margin:20px;">'
    )


def div_table():
    return (
        "<div style=\"font-size:24px;text-align:justify; font-family: 'Open Sans'; color:#000077;"
        + 'font-weight: 500;margin:20px;overflow:auto;width:100%;">'
    )


level = 0

def logging_decorator(func):
    def error_log():
        try:
            func()
        except Exception as err:
            logger.error(err, extra={'real_pathname': inspect.getsourcefile(func),  # path to source file
                                     'real_lineno': inspect.trace()[-1][2],         # line number from trace
                                     'real_funcName': func.__name__})               # function name

    return error_log




def log_method(method):
    """
    A decorator to log the name of a class method when it is executed.
    """

    def wrapper(self, *args, **kwargs):
        global level
        class_name = self.__class__.__name__
        ident = "⋅ " * level

        logger = logging.getLogger()
        source_file = inspect.getsourcefile(method)
        line_number = inspect.getsourcelines(method)[1]
        lr = logger.makeRecord(logger.name,
                               logging.DEBUG,
                               source_file,
                               line_number,
                               ident + f"{class_name}.{method.__name__}", {}, None, "")
        logger.handle(lr)

        level += 1
        if args or kwargs:
            result = method(self, *args, **kwargs)
        else:
            result = method(self)
        level -= 1
        # logging.debug(ident+f"<{class_name}.{method.__name__}")
        return result

    return wrapper


def log_method_noarg(method):
    """
    A decorator to log the name of a class method when it is executed.
    Signature is without extra arguments is enforced.
    To use when Qt passes different number of arguments depending on signature.
    """

    def wrapper(self):
        global level
        class_name = self.__class__.__name__
        ident = "⋅ " * level

        logger = logging.getLogger()
        source_file = inspect.getsourcefile(method)
        line_number = inspect.getsourcelines(method)[1]
        lr = logger.makeRecord(logger.name,
                               logging.DEBUG,
                               source_file,
                               line_number,
                               ident + f"{class_name}.{method.__name__}", {}, None, "")
        logger.handle(lr)

        level += 1
        result = method(self)
        level -= 1
        # logging.debug(ident+f"<{class_name}.{method.__name__}")
        return result

    return wrapper
