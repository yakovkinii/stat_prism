import numpy as np
import pandas as pd

from src.common.constant import MDASH


def smart_comma_join(items):
    if len(items) == 0:
        return ""

    if len(items) == 1:
        return items[0]

    if len(items) == 2:
        return f"{items[0]} and {items[1]}"

    return ", ".join(items[:-1]) + f", and {items[-1]}"


def format_statistic_apa(statistic, decimals=2):
    if np.isnan(statistic) or statistic is None:
        return MDASH
    return str(f"{round(statistic, decimals):.{decimals}f}".replace("0.", "."))


def format_p_apa(p, decimals=3):
    if np.isnan(p) or p is None:
        return MDASH
    if p < 0.001:
        return "&lt;&nbsp;.001"
    else:
        return f"{round(p, decimals):.{decimals}f}".replace("0.", ".")


def get_stars(p):
    if p < 0.001:
        return "***"
    elif p < 0.01:
        return "**"
    elif p < 0.05:
        return "*"
    else:
        return ""


def _count_significant_decimal_places(num, precision=10):
    """
    Returns the number of significant decimal places for a number.
    If the number is an integer, returns 0.
    """
    if isinstance(num, int):
        return 0

    # Absolute value to handle negative numbers
    num = abs(num)

    # Round the number to the given precision and convert to string
    str_num = f"{round(num, precision+1):.{precision}f}".rstrip("0")

    # If there's a decimal point, calculate the number of decimal places
    if "." in str_num:
        return len(str_num.split(".")[1])

    # No decimal places if not found
    return 0


def get_reasonable_digits(s: pd.Series):
    """
    Determine the maximum number of significant decimal places in the pandas Series.
    Returns the maximum decimal places found in the data, plus 1.
    """
    # Apply the function to count decimal places in each number of the Series
    decimal_places = s.dropna().apply(_count_significant_decimal_places)

    # Determine the maximum number of decimal places found
    max_decimals = decimal_places.max()

    # Determine decimals based on the range of the data
    data_range = s.max() - s.min()

    if data_range > 0:
        # Calculate decimals based on range and log10 scaling
        range_based_decimals = -round(np.log10(data_range / 10))
        max_decimals = max(max_decimals, range_based_decimals)

    return max_decimals + 1
