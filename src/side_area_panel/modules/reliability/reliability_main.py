#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import logging

import numpy as np
import pandas as pd

from src.common.decorators import log_function
from src.common.translations import t
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.mathematics.correlation.correlation import (
    calculate_correlations,
)
from src.side_area_panel.modules.common.result.html_result import Cell, HTMLTableV2, Row
from src.side_area_panel.modules.common.utility import format_r_apa, smart_comma_join
from src.side_area_panel.modules.correlation.correlation_result import (
    CORRELATION_TYPE_MAP,
    CorrelationType,
)
from src.side_area_panel.modules.reliability.reliability_result import (
    ReliabilityResult,
    ReliabilityStudyConfig,
)

# Reliability shares the correlation module's estimators (matching its naming/results).
_PANDAS_CORR = {
    CorrelationType.PEARSON: "pearson",
    CorrelationType.SPEARMAN: "spearman",
    CorrelationType.KENDALL: "kendall",
}
# Types that need dichotomous items (estimated from 2x2 tables).
_BINARY_TYPES = (CorrelationType.PHI, CorrelationType.TETRACHORIC)


def _fail(result: ReliabilityResult, message: str) -> ReliabilityResult:
    """Show a validation message to the user and log it, then stop."""
    logging.warning("Reliability: %s", message)
    result.set_error(message)
    return result


def cronbach_alpha(corr_matrix: np.ndarray) -> float:
    """Standardised Cronbach's alpha from an item correlation matrix."""
    k = corr_matrix.shape[0]
    if k < 2:
        return float("nan")
    trace = np.trace(corr_matrix)
    matrix_sum = np.sum(corr_matrix)
    if matrix_sum == 0:
        return float("nan")
    return (k / (k - 1)) * (1 - (trace / matrix_sum))


def _full_correlation_matrix(df: pd.DataFrame, kind: CorrelationType) -> pd.DataFrame:
    """Symmetric item correlation matrix (diagonal 1) using the correlation module's
    estimators, so reliability matches the Correlation analysis. `calculate_correlations`
    fills one triangle; we mirror it and set the diagonal to 1."""
    lower, _, _ = calculate_correlations(df, kind)
    arr = lower.to_numpy(dtype=float)
    arr = np.where(np.isnan(arr), arr.T, arr)  # mirror the filled triangle
    np.fill_diagonal(arr, 1.0)
    return pd.DataFrame(arr, index=df.columns, columns=df.columns)


def _alpha_level_key(alpha: float) -> str:
    if np.isnan(alpha):
        return "unacceptable"
    if alpha > 0.9:
        return "excellent"
    if alpha > 0.8:
        return "good"
    if alpha > 0.7:
        return "acceptable"
    if alpha > 0.6:
        return "questionable"
    if alpha > 0.5:
        return "poor"
    return "unacceptable"


@log_function
def recalculate_reliability_study(elements, result: ReliabilityResult) -> ReliabilityResult:
    """Validate the inputs, then estimate Cronbach's alpha for the scale and an
    'if item removed' table. Unexpected exceptions are handled centrally by the panel's
    recalculate()."""
    config: ReliabilityStudyConfig = result.config
    result.result_elements = []

    items = config.column_selector[0] if config.column_selector else None
    if not items or len(items) < 2:
        return _fail(result, t("reliability.error.min_items"))

    data = DATA_MANAGER.get_data_from_data_label(
        data_label=config.data_source,
        current_result_id=result.unique_id,
    )
    df = data.get_dataframe(columns=items, map_ordinal=True)

    correlation_type = CORRELATION_TYPE_MAP[config.correlation_type]
    show_verbal = 1 if config.verbal_indicators else 0

    if correlation_type in _PANDAS_CORR:
        correlation_matrix = df.corr(method=_PANDAS_CORR[correlation_type])
    else:
        # Phi/Tetrachoric require dichotomous items; rescale them to 0..1 first. Polychoric
        # and Kendall tau-c work on the ordinal items directly.
        if correlation_type in _BINARY_TYPES:
            if not all(df[col].nunique() <= 2 for col in df.columns):
                return _fail(result, t("reliability.msg.binary_required"))
            for col in df.columns:
                df[col] = df[col] - df[col].min()
                if df[col].max() != 0:
                    df[col] = df[col] / df[col].max()
        correlation_matrix = _full_correlation_matrix(df, correlation_type)

    corr_values = np.asarray(correlation_matrix.values, dtype=float)
    alpha = cronbach_alpha(corr_values)
    scale_name = (config.scale_name or "").strip() or t("reliability.scale_default")
    level_word = t(f"reliability.interpret.{_alpha_level_key(alpha)}")

    # ----- Cronbach's alpha table + verbal report -----
    alpha_table = HTMLTableV2(table_caption=t("reliability.caption.cronbach"))
    alpha_table.add_title_row_apa(
        Row(
            [Cell(), Cell(t("reliability.caption.cronbach"), center=True)]
            + [Cell(t("reliability.col.interpretation"), center=True)] * show_verbal
        )
    )
    alpha_table.add_single_row_apa(
        Row(
            [Cell(scale_name, push_to_left=True), Cell(format_r_apa(alpha), center=True)]
            + [Cell(level_word.capitalize(), center=True)] * show_verbal
        )
    )
    alpha_table.add_text(
        t(
            "reliability.report.main",
            scale=scale_name,
            n=len(items),
            level=level_word,
            alpha=format_r_apa(alpha),
        )
    )
    result.update_and_add_element(alpha_table, "reliability alpha")

    # ----- If item removed table -----
    # All quantities derive from the same item correlation matrix as the (standardised)
    # alpha, so they stay consistent across every correlation type (incl. polychoric):
    #   item-rest r = (sum of item's off-diagonal correlations) / sqrt(variance of the
    #   rest-sum), with all item variances = 1.
    item_table = HTMLTableV2(table_caption=t("reliability.caption.item_deleted"))
    item_table.add_title_row_apa(
        Row(
            [
                Cell(t("reliability.col.item"), push_to_left=True),
                Cell(t("reliability.col.item_total"), center=True),
                Cell(t("reliability.col.alpha_deleted"), center=True),
            ]
            + [Cell(t("reliability.col.improves"), center=True)] * show_verbal
        )
    )

    total_sum = corr_values.sum()
    row_sums = corr_values.sum(axis=1)
    improves = []
    for i, item in enumerate(df.columns):
        off_diagonal = row_sums[i] - corr_values[i, i]
        rest_variance = total_sum - 2 * row_sums[i] + corr_values[i, i]
        item_rest = off_diagonal / np.sqrt(rest_variance) if rest_variance > 0 else float("nan")
        sub = np.delete(np.delete(corr_values, i, axis=0), i, axis=1)
        alpha_deleted = cronbach_alpha(sub)
        item_improves = (not np.isnan(alpha_deleted)) and (not np.isnan(alpha)) and alpha_deleted > alpha
        if item_improves:
            improves.append(str(item))
        if np.isnan(alpha_deleted) or np.isnan(alpha):
            improves_text = "—"
        else:
            improves_text = t("verbal.yes") if item_improves else t("verbal.no")
        item_table.add_single_row_apa(
            Row(
                [
                    Cell(str(item), push_to_left=True),
                    Cell(format_r_apa(item_rest), center=True),
                    Cell(format_r_apa(alpha_deleted), center=True),
                ]
                + [Cell(improves_text, center=True)] * show_verbal
            )
        )

    if improves:
        item_table.add_text(t("reliability.report.item_improve", items=smart_comma_join(improves)))
    else:
        item_table.add_text(t("reliability.report.item_none"))
    result.update_and_add_element(item_table, "reliability item_deleted")

    provided_name = (config.scale_name or "").strip()
    result.title_context = provided_name if provided_name else ", ".join(str(i)[:16] for i in items)
    return result
