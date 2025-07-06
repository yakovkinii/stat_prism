#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#

import logging

import numpy as np
import pandas as pd
from scipy.stats import linregress

from src.common.constant import ColumnType
from src.common.decorators import log_function
from src.common.result.classes.plot_result import Band, Heatmap, Line, PlotV2, Scatter
from src.data_panel.data import Data
from src.mathematics.correlation.correlation import calculate_correlations
from src.modules.correlation.report import get_report
from src.modules.correlation.result import CorrelationResult, CorrelationType
from src.modules.correlation.table import get_table_compact, get_table_full


def to_full_matrix(df: pd.DataFrame) -> pd.DataFrame:
    full_matrix = df.copy()
    for i, col1 in enumerate(df.columns):
        for j, col2 in enumerate(df.columns):
            if i > j:
                full_matrix.loc[col2, col1] = df.loc[col1, col2]
            elif i == j:
                full_matrix.loc[col1, col2] = 1

    full_matrix = full_matrix.astype(float)
    return full_matrix


@log_function
def recalculate_correlation_study(data: Data, result: CorrelationResult) -> CorrelationResult:
    cfg = result.config
    df = data.get_dataframe(filters=result.config.filters, columns=result.config.selected_columns, map_ordinal=True)

    columns = list(df.columns)

    correlation_matrix, p_matrix, df_matrix = calculate_correlations(df, cfg.correlation_type)

    if cfg.compact:
        html_table = get_table_compact(columns, correlation_matrix, p_matrix, kind=cfg.correlation_type)
    else:
        html_table = get_table_full(columns, correlation_matrix, p_matrix, df_matrix, kind=cfg.correlation_type)

    # Verbal
    verbal = get_report(
        columns,
        correlation_matrix,
        p_matrix,
        df_matrix,
        report_non_significant=not cfg.report_only_significant,
        kind=cfg.correlation_type,
    )
    html_table.add_text(verbal)

    if any([data[col].column_type == ColumnType.ORDINAL for col in columns]) and (
        cfg.correlation_type == CorrelationType.PEARSON
    ):
        msg = "Warning: Ordinal data detected. Pearson correlation is not suitable for ordinal data."
        logging.warning(msg)
        html_table.add_text(msg)

    result.title_context = ", ".join([f"{col[:16]}" for col in cfg.selected_columns])
    result.result_elements = [html_table]

    if cfg.generate_heatmap:
        heatmap_plot = PlotV2(
            items=[
                Heatmap(
                    df=to_full_matrix(correlation_matrix),
                    p=to_full_matrix(p_matrix),
                    label="Correlations",
                )
            ],
            title="Correlation Matrix",
            plot_title="Correlation Matrix",
            x_axis_title="",
            y_axis_title="",
        )
        result.result_elements.append(heatmap_plot)

    if cfg.generate_plots:
        for i, name1 in enumerate(columns):
            for j, name2 in enumerate(columns):
                if i < j:
                    if cfg.report_only_significant and p_matrix.loc[name1, name2] > 0.05:
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

                    plot_result = PlotV2(
                        items=[plot, plot_band, plot_line],
                        title=f"Plot: {name1[:16]} vs {name2[:16]}",
                        plot_title=f"Correlation between {name1} and {name2}",
                        x_axis_title=name1,
                        y_axis_title=name2,
                    )
                    result.result_elements.append(plot_result)

    return result
