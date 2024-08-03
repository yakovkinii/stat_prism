import logging
from typing import Union

import pandas as pd

from src.core.crosstab.crosstab_result import CrosstabResult
from src.core.crosstab.table import get_table_compact
from src.core.filter.filter_result import FilterResult
from src.results_panel.results.common.html_element import HTMLResultElement


def calculate_crosstab(df, col1, col2):
    crosstab = pd.crosstab(df[col1], df[col2])
    return crosstab


def recalculate_crosstab_study(
    df: pd.DataFrame, result: CrosstabResult, filter_result: Union[FilterResult, None]
) -> CrosstabResult:
    logging.info("Recalculating crosstab study")

    config = result.config
    if len(config.selected_columns) != 2:
        result.result_elements[result.html] = HTMLResultElement()
        logging.info("Not enough columns selected")
        return result

    if filter_result is not None:
        query = filter_result.config.query
        logging.info(f"Applying filter query: {query}")
        try:
            df = df.query(query)
        except Exception as e:
            logging.error(f"Error filtering data: {e}")
            return result
    else:
        logging.info("No filter applied")

    df = df[config.selected_columns]

    # table_name = "1"
    columns = list(df.columns)

    crosstab_matrix = calculate_crosstab(df, columns[0], columns[1])

    html_table = get_table_compact(columns, crosstab_matrix)

    html_result_element = HTMLResultElement()
    html_result_element.items.append(html_table)

    result.title_context = ", ".join([f"{col[:8]}" if len(col) > 8 else col for col in config.selected_columns])
    result.result_elements = {result.html: html_result_element}

    return result
