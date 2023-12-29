import logging

import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QTableWidgetItem

from core.constants import NO_RESULT_SELECTED
from core.shared import result_container


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
            table {
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

    <body>
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


def load_data_to_table(dataframe, table_widget):
    table_widget.setRowCount(dataframe.shape[0])
    table_widget.setColumnCount(dataframe.shape[1])
    table_widget.setHorizontalHeaderLabels(dataframe.columns)

    for row in dataframe.iterrows():
        for col, value in enumerate(row[1]):
            table_widget.setItem(row[0], col, QTableWidgetItem(str(value)))


def round_to_significant_digits(num, n):
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
