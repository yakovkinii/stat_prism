#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import pandas as pd

from src.common.decorators import log_function
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.dp_impute.dp_impute_result import ImputeResult
from src.side_area_panel.modules.dp_impute.dp_impute_ui import Elements


def _missing_mask(series: pd.Series) -> pd.Series:
    """True where the cell is missing or blank -- captures both NaN and empty strings ""."""
    return series.isna() | (series.astype(str).str.strip() == "")


@log_function
def dp_impute_main(elements: Elements, result: ImputeResult, update):
    cfg = result.config
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    new_data = data.copy()
    # Default to a pass-through so downstream stays valid while inputs are incomplete.
    result.data = new_data
    result.filled_count = 0
    result.removed_count = 0

    selected = cfg.column_selector[0] if cfg.column_selector else None
    if not selected:
        elements.column_selector.set_alert(0)
        return result

    method = cfg.method or "Mean"

    if method == "Remove rows with missing":
        # Drop every row missing any selected column.
        keep = pd.Series(True, index=new_data[selected[0]].data_series.index)
        for column_name in selected:
            keep = keep & ~_missing_mask(new_data[column_name].data_series)
        result.removed_count = int((~keep).sum())
        for column in new_data.columns:
            column.data_series = column.data_series[keep]
        result.data = new_data
        return result

    filled = 0
    for column_name in selected:
        column = new_data[column_name]
        series = column.data_series
        missing = _missing_mask(series)
        n_missing = int(missing.sum())
        if n_missing == 0:
            continue

        if method in ("Mean", "Median"):
            numeric = pd.to_numeric(series, errors="coerce")
            if numeric.notna().sum() == 0:
                continue  # nothing to estimate from
            fill_value = numeric.mean() if method == "Mean" else numeric.median()
            column.data_series = numeric.where(~missing, fill_value)
        elif method == "Mode":
            present = series[~missing]
            if present.empty:
                continue
            fill_value = present.mode().iloc[0]
            column.data_series = series.where(~missing, fill_value)
        elif method == "Constant value":
            constant = cfg.constant_value
            if constant in (None, ""):
                elements.constant_value.set_alert()
                return result
            # Use a numeric constant when the column is numeric and the value parses.
            fill_value = constant
            if column.is_numeric:
                try:
                    fill_value = float(constant)
                except (TypeError, ValueError):
                    fill_value = constant
            column.data_series = series.where(~missing, fill_value)
        else:
            continue

        filled += n_missing

    result.filled_count = filled
    result.data = new_data
    return result
