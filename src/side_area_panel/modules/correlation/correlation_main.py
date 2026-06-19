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
    calculate_cross_correlations,
    calculate_partial_correlations,
    calculate_partial_cross_correlations,
)
from src.side_area_panel.modules.common.result.plot_result import (
    Band,
    Heatmap,
    Line,
    PlotV2,
    Scatter,
)
from src.side_area_panel.modules.correlation.report import get_cross_report, get_report
from src.side_area_panel.modules.correlation.correlation_result import (
    CORRELATION_TYPE_MAP,
    CorrelationResult,
    CorrelationType,
)
from src.side_area_panel.modules.correlation.table import (
    get_table_compact,
    get_table_cross,
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


def _pairwise_plot(df, name1, name2):
    """Scatter of (name1, name2) with an OLS regression line and its standard-error band."""
    scatter = Scatter(x=df[name1], y=df[name2], label=t("correlation.plot.points"))

    regression = linregress(df[name1], df[name2])
    slope, intercept = regression.slope, regression.intercept
    std_err, intercept_std_err = regression.stderr, regression.intercept_stderr

    x_min, x_max = df[name1].min(), df[name1].max()
    x_min, x_max = x_min - 0.1 * (x_max - x_min), x_max + 0.1 * (x_max - x_min)
    x_pred = np.linspace(x_min, x_max, 100)
    y_pred = intercept + slope * x_pred

    conf_dynamic = std_err * abs(x_pred - df[name1].mean())
    conf_interval = np.sqrt(intercept_std_err**2 + conf_dynamic**2)

    plot_line = Line(x=x_pred[1:-1], y=y_pred[1:-1], label=t("correlation.plot.regression_line"))
    plot_band = Band(
        x=x_pred,
        y1=y_pred - conf_interval,
        y2=y_pred + conf_interval,
        label=t("correlation.plot.band"),
    )
    return PlotV2(
        items=[scatter, plot_band, plot_line],
        title=t("correlation.plot.scatter_tab", a=name1[:16], b=name2[:16]),
        plot_title=t("correlation.plot.scatter_title", a=name1, b=name2),
        x_axis_title=name1,
        y_axis_title=name2,
    )


def _ordinal_pearson_warning(result, data, columns, kind, html_table):
    if any(data[col].column_type == ColumnType.ORDINAL for col in columns) and kind == CorrelationType.PEARSON:
        msg = t("correlation.warning.ordinal_pearson")
        logging.warning(msg)
        html_table.add_text(msg)


@log_function
def recalculate_correlation_study(elements, result: CorrelationResult, update) -> CorrelationResult:
    """Validate inputs, compute the correlation matrix for the chosen coefficient, and
    build the table + verbal report (+ optional heatmap and pairwise plots). When a Second
    variable set is given, a rectangular two-set (cross) matrix is produced instead.
    Unexpected exceptions are handled centrally by the panel's recalculate()."""
    cfg = result.config
    result.result_elements = []

    selected_columns = list(cfg.column_selector[0] or [])
    control_columns = cfg.column_selector[1] if len(cfg.column_selector) > 1 else []
    second_set = list(cfg.column_selector[2] or []) if len(cfg.column_selector) > 2 else []
    is_cross = len(second_set) > 0

    if is_cross:
        if len(selected_columns) < 1 or len(second_set) < 1:
            return _fail(result, t("correlation.error.cross_min"))
    elif len(selected_columns) < 2:
        return _fail(result, t("correlation.error.min_variables"))

    control_columns = [
        c for c in (control_columns or []) if c not in selected_columns and c not in second_set
    ]
    is_partial = len(control_columns) > 0

    kind = CORRELATION_TYPE_MAP[cfg.correlation_type]
    if is_partial and kind not in (CorrelationType.PEARSON, CorrelationType.SPEARMAN):
        return _fail(result, t("correlation.partial.method_error"))

    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )

    update(5)
    if is_cross:
        return _run_cross(result, cfg, data, selected_columns, second_set, control_columns, kind, is_partial, update)

    df = data.get_dataframe(columns=list(selected_columns) + list(control_columns), map_ordinal=True)

    columns = list(selected_columns)

    if is_partial:
        correlation_matrix, p_matrix, df_matrix = calculate_partial_correlations(
            df, columns, control_columns, kind
        )
    else:
        correlation_matrix, p_matrix, df_matrix = calculate_correlations(df[columns], kind)
    update(45)

    if cfg.compact:
        html_table = get_table_compact(columns, correlation_matrix, p_matrix, kind=kind)
    else:
        html_table = get_table_full(columns, correlation_matrix, p_matrix, df_matrix, kind=kind)

    # Verbal report (prefixed with a note when these are partial correlations)
    verbal = get_report(
        columns,
        correlation_matrix,
        p_matrix,
        df_matrix,
        report_non_significant=not cfg.report_only_significant,
        kind=kind,
    )
    if is_partial:
        verbal = t("correlation.partial.note", controls=", ".join(control_columns)) + verbal
    html_table.add_text(verbal)

    _ordinal_pearson_warning(result, data, columns, kind, html_table)

    result.title_context = ", ".join(col[:16] for col in columns)
    result.update_and_add_element(html_table, "correlation table")
    update(60)

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

    # Raw pairwise scatter/regression plots would contradict the partialled-out matrix,
    # so they are only drawn for ordinary (non-partial) correlations.
    if cfg.generate_plots and not is_partial:
        for i, name1 in enumerate(columns):
            for j, name2 in enumerate(columns):
                if i >= j:
                    continue
                if cfg.report_only_significant and p_matrix.loc[name1, name2] > 0.05:
                    continue
                result.update_and_add_element(
                    _pairwise_plot(df, name1, name2), f"correlation plot {name1} | {name2}"
                )
            update(60 + 35 * (i + 1) / len(columns))

    update(100)
    return result


def _run_cross(result, cfg, data, rows, cols, control_columns, kind, is_partial, update):
    """Rectangular two-set (cross) correlation: every variable in the first set against every
    variable in the second set, as a full rows×cols matrix."""
    all_columns = list(dict.fromkeys(list(rows) + list(cols) + list(control_columns)))
    df = data.get_dataframe(columns=all_columns, map_ordinal=True)

    if is_partial:
        correlation_matrix, p_matrix, df_matrix = calculate_partial_cross_correlations(
            df, rows, cols, control_columns, kind
        )
    else:
        correlation_matrix, p_matrix, df_matrix = calculate_cross_correlations(df, rows, cols, kind)
    update(45)

    html_table = get_table_cross(rows, cols, correlation_matrix, p_matrix, df_matrix, kind, compact=cfg.compact)

    verbal = get_cross_report(
        rows,
        cols,
        correlation_matrix,
        p_matrix,
        df_matrix,
        report_non_significant=not cfg.report_only_significant,
        kind=kind,
    )
    if is_partial:
        verbal = t("correlation.partial.note", controls=", ".join(control_columns)) + verbal
    html_table.add_text(verbal)

    _ordinal_pearson_warning(result, data, list(rows) + list(cols), kind, html_table)

    result.title_context = ", ".join(c[:16] for c in rows) + " × " + ", ".join(c[:16] for c in cols)
    result.update_and_add_element(html_table, "correlation table")
    update(60)

    if cfg.generate_heatmap:
        # Rectangular matrix -> pass directly (no square-completion).
        heatmap_plot = PlotV2(
            items=[
                Heatmap(
                    df=correlation_matrix.astype(float),
                    p=p_matrix.astype(float),
                    label="Correlations",
                )
            ],
            title=t("correlation.plot.matrix_title"),
            plot_title=t("correlation.plot.matrix_title"),
            x_axis_title="",
            y_axis_title="",
        )
        result.update_and_add_element(heatmap_plot, "correlation heatmap")

    if cfg.generate_plots and not is_partial:
        for step, name1 in enumerate(rows):
            for name2 in cols:
                if name1 == name2:
                    continue
                if cfg.report_only_significant and p_matrix.loc[name1, name2] > 0.05:
                    continue
                result.update_and_add_element(
                    _pairwise_plot(df, name1, name2), f"correlation plot {name1} | {name2}"
                )
            update(60 + 35 * (step + 1) / len(rows))

    update(100)
    return result
