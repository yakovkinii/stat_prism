import logging
from typing import Union

import pandas as pd
from scipy.stats import pearsonr

from src.core.correlation.correlation_result import CorrelationResult
from src.core.correlation.report import get_report
from src.core.correlation.table import get_table_compact, get_table_full
from src.core.filter.filter_result import FilterResult
from src.results_panel.results.common.html_element import HTMLResultElement, HTMLText
from src.results_panel.results.common.plot_element import PlotResultElement, Scatter


def calculate_correlations(df):
    correlation_matrix = pd.DataFrame(index=df.columns, columns=df.columns)
    p_matrix = pd.DataFrame(index=df.columns, columns=df.columns)
    df_matrix = pd.DataFrame(index=df.columns, columns=df.columns)

    # Calculate correlation, p-values, and degrees of freedom for each pair of columns
    for i1, col1 in enumerate(df.columns):
        for i2, col2 in enumerate(df.columns):
            if i1 <= i2:
                continue
            # Drop NA values for the pair of columns
            valid_data = df[[col1, col2]].dropna()

            # Compute correlation and p-value
            corr, p_value = pearsonr(valid_data[col1], valid_data[col2])

            # Calculate degrees of freedom (n - 2)
            degrees_of_freedom = len(valid_data) - 2

            # Fill the square matrix
            correlation_matrix.loc[col1, col2] = corr
            p_matrix.loc[col1, col2] = p_value
            df_matrix.loc[col1, col2] = degrees_of_freedom

    return correlation_matrix, p_matrix, df_matrix


def recalculate_correlation_study(
    df: pd.DataFrame, result: CorrelationResult, filter_result: Union[FilterResult, None]
) -> CorrelationResult:
    logging.info("Recalculating correlation study")

    config = result.config
    if len(config.selected_columns) < 2:
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

    compact = config.compact
    table_name = "1"
    report_only_significant = config.report_only_significant
    columns = list(df.columns)

    correlation_matrix, p_matrix, df_matrix = calculate_correlations(df)

    # html_table = get_table(columns, correlation_matrix, p_matrix, df_matrix, compact, table_name)
    if compact:
        html_table = get_table_compact(columns, correlation_matrix, p_matrix)
    else:
        html_table = get_table_full(columns, correlation_matrix, p_matrix, df_matrix)

    # Verbal
    verbal = get_report(
        columns, correlation_matrix, p_matrix, df_matrix, table_name, report_non_significant=not report_only_significant
    )
    html_result_element = HTMLResultElement()
    html_result_element.items.append(html_table)
    html_result_element.items.append(HTMLText(verbal))

    result.title_context = ", ".join([f"{col[:8]}" if len(col) > 8 else col for col in config.selected_columns])
    result.result_elements = {result.html: html_result_element}

    # Add plots
    for i, name1 in enumerate(columns):
        for j, name2 in enumerate(columns):
            if i < j:
                if report_only_significant and p_matrix.loc[name1, name2] > 0.05:
                    continue
                plot = Scatter(
                    x=df[name1],
                    y=df[name2],
                )
                plot_result = PlotResultElement(
                    tab_title=f"{name1[:8]} vs {name2[:8]}",
                    plot_title=f"Correlation between {name1} and {name2}",
                    x_axis_title=name1,
                    y_axis_title=name2,
                )
                plot_result.items = [plot]

                result.result_elements[str(i) + "_" + str(j)] = plot_result

    return result
