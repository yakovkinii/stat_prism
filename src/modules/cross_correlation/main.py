import logging

import numpy as np
import pandas as pd
from scipy.stats import kendalltau, linregress, pearsonr, spearmanr

from src.common.result.classes.html_result import HTMLResultElement, HTMLText
from src.common.result.classes.plot_result import Band, Line, PlotResultElement, Scatter
from src.modules.cross_correlation.report import get_report
from src.modules.cross_correlation.result import (
    CrossCorrelationResult,
    CrossCorrelationStudyConfig,
    CrossCorrelationType,
)
from src.modules.cross_correlation.table import get_table_compact, get_table_full
from src.settings_panel.panels.registry import PanelRegistry


def calculate_cross_correlations(df1, df2, kind: CrossCorrelationType):
    correlation_matrix = pd.DataFrame(index=df1.columns, columns=df2.columns)
    p_matrix = pd.DataFrame(index=df1.columns, columns=df2.columns)
    df_matrix = pd.DataFrame(index=df1.columns, columns=df2.columns)

    # Calculate correlation, p-values, and degrees of freedom for each pair of columns
    for i1, col1 in enumerate(df1.columns):
        for i2, col2 in enumerate(df2.columns):
            if kind == CrossCorrelationType.PEARSON:
                # Compute correlation and p-value
                corr, p_value = pearsonr(df1[col1], df2[col2])
            elif kind == CrossCorrelationType.SPEARMAN:
                corr, p_value = spearmanr(df1[col1], df2[col2])
            elif kind == CrossCorrelationType.KENDALL:
                corr, p_value = kendalltau(df1[col1], df2[col2])
            else:
                raise ValueError(f"Invalid correlation type: {kind}")

            # Calculate degrees of freedom (n - 2)
            degrees_of_freedom = len(df1) - 2

            # Fill the square matrix
            correlation_matrix.loc[col1, col2] = corr
            p_matrix.loc[col1, col2] = p_value
            df_matrix.loc[col1, col2] = degrees_of_freedom

    return correlation_matrix, p_matrix, df_matrix


def recalculate_cross_correlation_study(df: pd.DataFrame, result: CrossCorrelationResult) -> CrossCorrelationResult:
    logging.info("Recalculating correlation study")

    config: CrossCorrelationStudyConfig = result.config
    if len(config.selected_columns1) < 2 or len(config.selected_columns2) < 1:
        result.set_elements(
            HTMLResultElement(
                settings_panel_index=PanelRegistry.HTML_RESULT_ITEM_SETTINGS.settings_stacked_widget_index
            ),
            {},
        )
        logging.info("Not enough columns selected")
        return result

    if len(config.filters) > 0:
        for filter_settings in config.filters:
            df = df.query(filter_settings.get_query())
    else:
        logging.info("No filter applied")

    df1 = df[config.selected_columns1]
    df2 = df[config.selected_columns2]

    compact = config.compact
    report_only_significant = config.report_only_significant
    kind = config.cross_correlation_type
    rows = list(df1.columns)
    columns = list(df2.columns)

    correlation_matrix, p_matrix, df_matrix = calculate_cross_correlations(df1, df2, kind)

    if compact:
        html_table = get_table_compact(rows, columns, correlation_matrix, p_matrix, kind=kind)
    else:
        html_table = get_table_full(rows, columns, correlation_matrix, p_matrix, df_matrix, kind=kind)

    # Verbal
    verbal = get_report(
        rows,
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

    html_result_element.items.append(html_table)
    html_result_element.items.append(HTMLText(verbal))
    html_result_element.set_table_id("1")
    html_result_element.table_caption = html_table.table_caption

    result.title_context = (
        ", ".join([f"{col[:16]}" for col in config.selected_columns1])
        + "\n"
        + ", ".join([f"{col[:16]}" for col in config.selected_columns2])
    )

    if not config.generate_plots:
        result.set_elements(html_result_element, {})
        return result

    plot_result_elements = {}
    # Add plots
    for i, name1 in enumerate(rows):
        for j, name2 in enumerate(columns):
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
            name = f"{i}_{j}"
            while name in plot_result_elements:
                name += "_"
            plot_result_elements[name] = plot_result

    result.set_elements(html_result_element, plot_result_elements)

    return result
