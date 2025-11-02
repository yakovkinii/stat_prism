#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import numpy as np

from src.common.constant import MDASH


def smart_comma_join(items):
    if len(items) == 0:
        return ""

    if len(items) == 1:
        return items[0]

    if len(items) == 2:
        return f"{items[0]} and {items[1]}"

    return ", ".join(items[:-1]) + f", and {items[-1]}"


def format_value_apa(value, decimals=1):
    if isinstance(value, str):
        return value
    if np.isnan(value) or value is None:
        return MDASH
    return str(f"{round(value, decimals):.{decimals}f}")


def format_statistic_apa(statistic, decimals=2):
    if isinstance(statistic, str):
        return statistic
    if np.isnan(statistic) or statistic is None:
        return MDASH
    return str(f"{round(statistic, decimals):.{decimals}f}")


def format_p_apa(p, decimals=3, add_equals=False):
    if isinstance(p, str):
        return "= " * add_equals + p
    if np.isnan(p) or p is None:
        return MDASH
    if p < 0.001:
        return "&lt;&nbsp;.001"
    if p < 0.01:
        return "&lt;&nbsp;.01"
    if p < 0.05:
        return "&lt;&nbsp;.05"
    return "= " * add_equals + f"{round(p, decimals):.{decimals}f}".replace("0.", ".")


def format_p_apa_full(p, decimals=3):
    if np.isnan(p) or p is None:
        return MDASH
    if p < 0.001:
        return "p&lt;.001"
    if p < 0.01:
        return "p&lt;.01"
    if p < 0.05:
        return "p&lt;.05"
    return f"p={round(p, decimals):.{decimals}f}".replace("0.", ".")
