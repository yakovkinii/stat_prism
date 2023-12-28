import logging

import numpy as np
import pandas as pd


def smart_comma_join(items):
    if len(items) == 0:
        return ""

    if len(items) == 1:
        return items[0]

    if len(items) == 2:
        return f"{items[0]} and {items[1]}"

    return ", ".join(items[:-1]) + f", and {items[-1]}"


def round_to_significant_digits(num, n):
    if num == 0:
        return 0  # Handle the special case where the number is zero
    else:
        return round(num, -int(np.floor(np.log10(abs(num))) - (n - 1)))


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

        return round(num, -int(np.floor(np.log10(abs(num))) - (digits - 1)))
        # return f"{whole}.{decimal[:digits-len(whole)]}"  # Taking the first three characters of the decimal part
    else:
        return whole


def round_series(series: pd.Series, n=4):
    return series.apply(round_to_significant_digits, args=(n,))


def div_title():
    return (
        f"<div style=\"font-size:32px;text-align:center; font-family: 'Open Sans'; color:#000077;"
        + f'font-weight: 500;margin:20px;">'
    )


def div_text():
    return (
        f"<div style=\"font-size:24px;text-align:justify; font-family: 'Open Sans'; color:#000077;"
        + f'font-weight: 500;margin:20px;">'
    )


def div_table():
    return (
        f"<div style=\"font-size:24px;text-align:justify; font-family: 'Open Sans'; color:#000077;"
        + f'font-weight: 500;margin:20px;overflow:auto;width:100%;">'
    )
