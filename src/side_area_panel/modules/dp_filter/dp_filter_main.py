#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import operator
import re

import pandas as pd

from src.common.decorators import log_function
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.iispwac.iispwac_column_filter import EMPTY_SENTINEL
from src.side_area_panel.modules.dp_filter.dp_filter_result import FilterDataResult
from src.side_area_panel.modules.dp_filter.dp_filter_ui import Elements

_NUMERIC_OPS = {
    "<": operator.lt,
    ">": operator.gt,
    "<=": operator.le,
    ">=": operator.ge,
}


def _parse_numeric_values(text):
    """Split on commas, semicolons and whitespace into a list of floats."""
    tokens = [token for token in re.split(r"[,;\s]+", text.strip()) if token != ""]
    return [float(token) for token in tokens]


def _empty_mask(series: pd.Series) -> pd.Series:
    """True where the cell is missing or blank -- captures both NaN and empty strings ""."""
    return series.isna() | (series.astype(str).str.strip() == "")


def _set_no_filter(result, data):
    """Pass-through: keep every row, and record an empty removed set for the popup."""
    result.data = data.copy()
    result.full_data = data.copy()
    result.removed_positions = []
    return result


@log_function
def dp_filter_main(elements: Elements, result: FilterDataResult, update):
    cfg = result.config
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )

    # Disabled filter is a no-op but still occupies its slot in the data chain.
    if not cfg.enabled:
        return _set_no_filter(result, data)

    selected = cfg.column_selector[0]
    if not selected:
        elements.column_selector.set_alert(0)
        return _set_no_filter(result, data)
    column_name = selected[0]

    spec = cfg.column_filter
    if spec is None or spec.get("column") != column_name:
        # Not configured for the current column yet -> no-op.
        return _set_no_filter(result, data)

    series = data[column_name].data_series
    mode = spec.get("mode")
    mask = None

    if mode == "numeric":
        operation = spec.get("operation")
        if operation in ("is empty", "is not empty"):
            empties = _empty_mask(series)
            mask = empties if operation == "is empty" else ~empties
        else:
            value_text = spec.get("value")
            if value_text in (None, ""):
                return _set_no_filter(result, data)
            numeric = pd.to_numeric(series, errors="coerce")
            if operation in ("==", "!="):
                # Accept multiple values (space/comma/semicolon separated) -> in / not in.
                try:
                    values = _parse_numeric_values(value_text)
                except ValueError:
                    elements.column_filter.set_alert()
                    return _set_no_filter(result, data)
                if not values:
                    return _set_no_filter(result, data)
                is_in = numeric.isin(values)
                mask = is_in if operation == "==" else ~is_in
            else:
                op = _NUMERIC_OPS.get(operation)
                if op is None:
                    return _set_no_filter(result, data)
                try:
                    value = float(value_text)
                except (TypeError, ValueError):
                    elements.column_filter.set_alert()
                    return _set_no_filter(result, data)
                mask = op(numeric, value).fillna(False)
    elif mode == "categorical":
        kept = spec.get("kept_values")
        if kept is None:
            return _set_no_filter(result, data)  # all values kept -> no-op
        # The "(empty)" pseudo-value keeps missing/blank cells; real values match directly.
        keep_empty = EMPTY_SENTINEL in kept
        real_kept = [v for v in kept if v != EMPTY_SENTINEL]
        mask = series.isin(real_kept)
        if keep_empty:
            mask = mask | _empty_mask(series)
    else:
        return _set_no_filter(result, data)

    if mask is None:
        return _set_no_filter(result, data)

    mask = mask.astype(bool)
    # Record the removed row positions (relative to the unfiltered row order) for the popup.
    result.full_data = data.copy()
    result.removed_positions = [i for i, keep in enumerate(mask.tolist()) if not keep]

    new_data = data.copy()
    for column in new_data.columns:
        column.data_series = column.data_series[mask]
    result.data = new_data
    return result
