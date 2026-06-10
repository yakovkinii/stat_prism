#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import logging

import numpy as np
import pandas as pd
from scipy.stats import linregress

from src.common.constant import ColumnType
from src.common.decorators import log_function
from src.common.translations import t
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.mathematics.correlation.correlation import (
    calculate_correlations,
)
from src.side_area_panel.modules.common.result.plot_result import (
    Band,
    Heatmap,
    Line,
    PlotV2,
    Scatter,
)
from src.side_area_panel.modules.correlation.report import get_report
from src.side_area_panel.modules.correlation.result import (
    CORRELATION_TYPE_MAP,
    CorrelationResult,
    CorrelationType,
)
from src.side_area_panel.modules.correlation.table import (
    get_table_compact,
    get_table_full,
)


def _fail(result: CorrelationResult, message: str) -> CorrelationResult:
    """Show a validation message to the user and log it, then stop."""
    logging.warning("Correlation: %s", message)
    result.set_error(message)
    return result


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
def recalculate_correlation_study(elements, result: CorrelationResult) -> CorrelationResult:
    """Validate inputs, compute the correlation matrix for the chosen coefficient, and
    build the table + verbal report (+ optional heatmap and pairwise plots). Unexpected
    exceptions are handled centrally by the panel's recalculate()."""
    cfg = result.config
    result.result_elements = []

    selected_columns = cfg.column_selector[0]
    if not selected_columns or len(selected_columns) < 2:
        return _fail(result, t("correlation.error.min_variables"))

    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    df = data.get_dataframe(columns=selected_columns, map_ordinal=True)

    columns = list(df.columns)
    kind = CORRELATION_TYPE_MAP[cfg.correlation_type]

    correlation_matrix, p_matrix, df_matrix = calculate_correlations(df, kind)

    if cfg.compact:
        html_table = get_table_compact(columns, correlation_matrix, p_matrix, kind=kind)
    else:
        html_table = get_table_full(columns, correlation_matrix, p_matrix, df_matrix, kind=kind)

    # Verbal report
    verbal = get_report(
        columns,
        correlation_matrix,
        p_matrix,
        df_matrix,
        report_non_significant=not cfg.report_only_significant,
        kind=kind,
    )
    html_table.add_text(verbal)

    if any(data[col].column_type == ColumnType.ORDINAL for col in columns) and kind == CorrelationType.PEARSON:
        msg = t("correlation.warning.ordinal_pearson")
        logging.warning(msg)
        html_table.add_text(msg)

    result.title_context = ", ".join(col[:16] for col in columns)
    result.update_and_add_element(html_table, "correlation table")

    if cfg.generate_heatmap:
        heatmap_plot = PlotV2(
            items=[
                Heatmap(
                    df=to_full_matrix(correlation_matrix),
                    p=to_full_matrix(p_matrix),
                    label="Correlations",
                )
            ],
            title=t("correlation.plot.matrix_title"),
            plot_title=t("correlation.plot.matrix_title"),
            x_axis_title="",
            y_axis_title="",
        )
        result.update_and_add_element(heatmap_plot, "correlation heatmap")

    if cfg.generate_plots:
        for i, name1 in enumerate(columns):
            for j, name2 in enumerate(columns):
                if i >= j:
                    continue
                if cfg.report_only_significant and p_matrix.loc[name1, name2] > 0.05:
                    continue
                scatter = Scatter(x=df[name1], y=df[name2], label="Scatter: data points")

                # Regression line + standard-error band
                regression = linregress(df[name1], df[name2])
                slope, intercept = regression.slope, regression.intercept
                std_err, intercept_std_err = regression.stderr, regression.intercept_stderr

                x_min, x_max = df[name1].min(), df[name1].max()
                x_min, x_max = x_min - 0.1 * (x_max - x_min), x_max + 0.1 * (x_max - x_min)
                x_pred = np.linspace(x_min, x_max, 100)
                y_pred = intercept + slope * x_pred

                conf_dynamic = std_err * abs(x_pred - df[name1].mean())
                conf_interval = np.sqrt(intercept_std_err**2 + conf_dynamic**2)

                plot_line = Line(x=x_pred[1:-1], y=y_pred[1:-1], label="Line: linear regression")
                plot_band = Band(
                    x=x_pred,
                    y1=y_pred - conf_interval,
                    y2=y_pred + conf_interval,
                    label="Band: Standard Error",
                )

                plot_result = PlotV2(
                    items=[scatter, plot_band, plot_line],
                    title=t("correlation.plot.scatter_tab", a=name1[:16], b=name2[:16]),
                    plot_title=t("correlation.plot.scatter_title", a=name1, b=name2),
                    x_axis_title=name1,
                    y_axis_title=name2,
                )
                result.update_and_add_element(plot_result, f"correlation plot {name1} | {name2}")

    return result
