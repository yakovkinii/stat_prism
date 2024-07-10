import pandas as pd
import scipy.stats

from src.core.correlation.report import get_report
from src.core.correlation.table import get_table_compact, get_table_full
from src.results_panel.results.common.html_element import HTMLResultElement, HTMLText
from src.core.correlation.correlation_result import CorrelationResult


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
        result.result_elements[result.html] = HTMLResultElement()
        return result
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
    verbal = get_report(columns, correlation_matrix, p_matrix, df_matrix, table_name, report_non_significant=not report_only_significant)
    html_result_element = HTMLResultElement()
    html_result_element.items.append(html_table)
    html_result_element.items.append(HTMLText(verbal))

    result.result_elements[result.html] = html_result_element
    return result

