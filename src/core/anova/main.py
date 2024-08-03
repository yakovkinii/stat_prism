import logging
from typing import Union

import pandas as pd
from sklearn.linear_model import LinearRegression

from src.core.anova.anova_result import AnovaResult
from src.core.filter.filter_result import FilterResult
from src.results_panel.results.common.html_element import HTMLResultElement, HTMLText


def calculate_anova(df, col1, col2):
    anova = LinearRegression()
    anova.fit(df[col1].values.reshape(-1, 1), df[col2].values.reshape(-1, 1))
    a = anova.intercept_
    b = anova.coef_[0]
    return a, b


def recalculate_anova_study(
    df: pd.DataFrame, result: AnovaResult, filter_result: Union[FilterResult, None]
) -> AnovaResult:
    logging.info("Recalculating anova study")

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

    columns = list(df.columns)

    a, b = calculate_anova(df, columns[0], columns[1])

    html_result_element = HTMLResultElement()
    html_result_element.items.append(HTMLText(f"linear chotatut anova a={a}, b={b}"))

    result.title_context = ", ".join([f"{col[:8]}" if len(col) > 8 else col for col in config.selected_columns])
    result.result_elements = {result.html: html_result_element}

    return result
