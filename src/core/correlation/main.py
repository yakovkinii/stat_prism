import numpy as np
import pandas as pd
import scipy.stats

from src.common.utility import smart_comma_join
from src.core.correlation.report import get_report
from src.core.correlation.table import get_table
from src.results_panel.results.correlation.correlation_result import CorrelationResult


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
            corr, p_value = scipy.stats.pearsonr(valid_data[col1], valid_data[col2])

            # Calculate degrees of freedom (n - 2)
            degrees_of_freedom = len(valid_data) - 2

            # Fill the square matrix
            correlation_matrix.loc[col1, col2] = corr
            p_matrix.loc[col1, col2] = p_value
            df_matrix.loc[col1, col2] = degrees_of_freedom

    return correlation_matrix, p_matrix, df_matrix


def recalculate_correlation_study(
    df: pd.DataFrame, result: CorrelationResult
) -> CorrelationResult:
    config = result.config
    if len(config.selected_columns) < 2:
        result.result_elements[result.table].html = "Please select at least 2 columns to analyse"
        result.result_elements[result.description].text = "Please select at least 2 columns to analyse"
        return result
    df = df[config.selected_columns]

    compact = False
    table_name = "1"
    report_non_significant = True
    columns = list(df.columns)

    correlation_matrix, p_matrix, df_matrix = calculate_correlations(df)

    html_table = get_table(columns, correlation_matrix, p_matrix, df_matrix, compact, table_name)

    # Plot
    # name1 = readable.iloc[0, 0] if readable.iloc[0, 2] > -readable.iloc[-1, 2] else readable.iloc[-1, 0]
    # name2 = readable.iloc[0, 1] if readable.iloc[0, 2] > -readable.iloc[-1, 2] else readable.iloc[-1, 1]
    # name1 = columns[0]
    # name2 = columns[1]
    # df_plot = df.loc[:, [name1, name2]]
    # plot_result = PlotResultItem(df_plot[[name1, name2]], f"Plot (Study #{result_id}):")
    # plot_result.x_axis_title = name1
    # plot_result.y_axis_title = name2
    # result.items.append(plot_result)

    # Verbal
    verbal = get_report(columns, correlation_matrix, p_matrix, df_matrix, table_name, report_non_significant)
    result.result_elements[result.table].html = html_table
    result.result_elements[result.description].text = verbal

    return result

