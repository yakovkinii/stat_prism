#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import operator
import re

import pandas as pd

from src.common.decorators import log_function
from src.data.data_manager import DATA_MANAGER
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


@log_function
def dp_filter_main(elements: Elements, result: FilterDataResult, update):
    cfg = result.config
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    # Default to a pass-through so downstream stays valid.
    result.data = data.copy()

    # Disabled filter is a no-op but still occupies its slot in the data chain.
    if not cfg.enabled:
        return result

    selected = cfg.column_selector[0]
    if not selected:
        elements.column_selector.set_alert(0)
        return result
    column_name = selected[0]

    spec = cfg.column_filter
    if spec is None or spec.get("column") != column_name:
        # Not configured for the current column yet -> no-op.
        return result

    new_data = data.copy()
    series = new_data[column_name].data_series
    mode = spec.get("mode")

    if mode == "numeric":
        value_text = spec.get("value")
        if value_text in (None, ""):
            return result
        operation = spec.get("operation")
        numeric = pd.to_numeric(series, errors="coerce")

        if operation in ("==", "!="):
            # Accept multiple values (space/comma/semicolon separated) -> in / not in.
            try:
                values = _parse_numeric_values(value_text)
            except ValueError:
                elements.column_filter.set_alert()
                return result
            if not values:
                return result
            is_in = numeric.isin(values)
            mask = is_in if operation == "==" else ~is_in
        else:
            op = _NUMERIC_OPS.get(operation)
            if op is None:
                return result
            try:
                value = float(value_text)
            except (TypeError, ValueError):
                elements.column_filter.set_alert()
                return result
            mask = op(numeric, value).fillna(False)
    elif mode == "categorical":
        kept = spec.get("kept_values")
        if kept is None:
            return result  # all values kept -> no-op
        mask = series.isin(kept)
    else:
        return result

    for column in new_data.columns:
        column.data_series = column.data_series[mask]
    result.data = new_data
    return result
