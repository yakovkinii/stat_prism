import logging
from typing import Dict, Union

import numpy as np
import pandas as pd
from scipy.stats import kendalltau, linregress, pearsonr, spearmanr

from src.common.decorators import log_function
from src.common.result.classes.html_result import HTMLResultElement, HTMLText
from src.common.result.classes.plot_result import Band, Line, PlotResultElement, Scatter
from src.modules.correlation.binary_correlations import phi_coefficient, tetrachoric_corr_2x2_table
from src.modules.correlation.report import get_report
from src.modules.correlation.result import CorrelationResult, CorrelationStudyConfig, CorrelationType
from src.modules.correlation.table import get_table_compact, get_table_full
from src.settings_panel.panels.registry import PanelRegistry


def calculate_correlations(df, kind: CorrelationType):
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

            if kind == CorrelationType.PEARSON:
                # Compute correlation and p-value
                corr, p_value = pearsonr(valid_data[col1], valid_data[col2])
                degrees_of_freedom = len(valid_data) - 2
            elif kind == CorrelationType.SPEARMAN:
                corr, p_value = spearmanr(valid_data[col1], valid_data[col2])
                degrees_of_freedom = np.nan  # Not available
            elif kind == CorrelationType.KENDALL:
                corr, p_value = kendalltau(valid_data[col1], valid_data[col2])
                degrees_of_freedom = np.nan  # Not available
            elif kind == CorrelationType.PHI:
                corr, p_value, degrees_of_freedom = phi_coefficient(valid_data[col1], valid_data[col2])
            elif kind == CorrelationType.TETRACHORIC:
                corr, _, p_value, degrees_of_freedom = tetrachoric_corr_2x2_table(
                    table=pd.crosstab(df.iloc[:, 0], df.iloc[:, 1]).values
                )
            else:
                raise ValueError(f"Invalid correlation type: {kind}")

            # Fill the square matrix
            correlation_matrix.loc[col1, col2] = corr
            p_matrix.loc[col1, col2] = p_value
            df_matrix.loc[col1, col2] = degrees_of_freedom

    return correlation_matrix, p_matrix, df_matrix


@log_function
def recalculate_correlation_study(
    df: pd.DataFrame, result: CorrelationResult, ordinal_orders: Dict[str, Dict[Union[int, float, str], int]]
) -> CorrelationResult:
    logging.info("Recalculating correlation study")

    config: CorrelationStudyConfig = result.config
    if len(config.selected_columns) < 2:
        msg = "Please select at least two Variables"
        result.set_placeholder(msg)
        logging.debug(msg)
        return result

    if len(config.filters) > 0:
        for filter_settings in config.filters:
            query = filter_settings.get_query()
            logging.debug(f"Applying Filter: {query}")
            df = df.query(query)
    else:
        logging.debug("No filter applied")

    compact = config.compact
    report_only_significant = config.report_only_significant
    kind = config.correlation_type

    df = df[config.selected_columns].copy()

    for col, ordinal_order in ordinal_orders.items():
        df[col] = df[col].map(ordinal_order)

    if kind in [CorrelationType.PHI, CorrelationType.TETRACHORIC]:
        if not all(df[col].nunique() <= 2 for col in df.columns):
            msg = f"All columns must have at most 2 unique values for {kind.name} correlation."
            result.set_placeholder(msg)
            logging.debug(msg)
            return result

    columns = list(df.columns)

    correlation_matrix, p_matrix, df_matrix = calculate_correlations(df, kind)

    # html_table = get_table(columns, correlation_matrix, p_matrix, df_matrix, compact, table_name)
    if compact:
        html_table = get_table_compact(columns, correlation_matrix, p_matrix, kind=kind)
    else:
        html_table = get_table_full(columns, correlation_matrix, p_matrix, df_matrix, kind=kind)

    # Verbal
    verbal = get_report(
        columns,
        correlation_matrix,
        p_matrix,
        df_matrix,
        report_non_significant=not report_only_significant,
        kind=kind,
    )
    html_result_element = HTMLResultElement(
        settings_panel_index=PanelRegistry.HTML_RESULT_ITEM_SETTINGS.settings_stacked_widget_index
    )
    if (len(ordinal_orders) > 0) and (kind == CorrelationType.PEARSON):
        msg = "Warning: Ordinal data detected. Pearson correlation is not suitable for ordinal data."
        logging.warning(msg)
        html_result_element.items.append(HTMLText(msg))

    html_result_element.items.append(html_table)
    html_result_element.items.append(HTMLText(verbal))
    html_result_element.table_caption = html_table.table_caption

    result.title_context = ", ".join([f"{col[:16]}" for col in config.selected_columns])

    if not config.generate_plots:
        result.result_elements = [html_result_element]
        return result

    plot_result_elements = []
    # Add plots
    for i, name1 in enumerate(columns):
        for j, name2 in enumerate(columns):
            if i < j:
                if report_only_significant and p_matrix.loc[name1, name2] > 0.05:
                    continue
                plot = Scatter(x=df[name1], y=df[name2], label=f"Scatter: data points")

                # Calculate the regression line
                result_linregress = linregress(df[name1], df[name2])
                slope, intercept, _, _, std_err, intercept_std_err = (
                    result_linregress.slope,
                    result_linregress.intercept,
                    result_linregress.rvalue,
                    result_linregress.pvalue,
                    result_linregress.stderr,
                    result_linregress.intercept_stderr,
                )
                x_min = df[name1].min()
                x_max = df[name1].max()
                x_min, x_max = x_min - 0.1 * (x_max - x_min), x_max + 0.1 * (x_max - x_min)

                x_pred = np.linspace(x_min, x_max, 100)
                y_pred = intercept + slope * x_pred

                # Calculate the confidence intervals
                conf_static = intercept_std_err
                conf_dynamic = std_err * abs(x_pred - df[name1].mean())
                conf_interval = np.sqrt(conf_static**2 + conf_dynamic**2)

                plot_line = Line(
                    x=x_pred[1:-1],
                    y=y_pred[1:-1],
                    label=f"Line: linear regression",
                )

                plot_band = Band(
                    x=x_pred,
                    y1=y_pred - conf_interval,
                    y2=y_pred + conf_interval,
                    label="Band: Standard Error",
                )

                plot_result = PlotResultElement(
                    settings_panel_index=PanelRegistry.PLOT_RESULT_ITEM_SETTINGS.settings_stacked_widget_index,
                    tab_title=f"Plot: {name1[:16]} vs {name2[:16]}",
                    plot_title=f"Correlation between {name1} and {name2}",
                    x_axis_title=name1,
                    y_axis_title=name2,
                )
                plot_result.items = [plot, plot_band, plot_line]
                plot_result_elements.append(plot_result)

    result.result_elements = [html_result_element] + plot_result_elements
    return result
