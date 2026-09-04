#  Copyright (C) 2023-2026  StatPrism Team
#  Balashevych A. K., Petrova N. V., Yakovkin I. I.
#
#  This file is part of StatPrism.
#
#  StatPrism is free software: you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  StatPrism is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  StatPrism.  If not, see <https://www.gnu.org/licenses/>.


# Pure filtering logic shared by the Filter data-processing module (dp_filter_main) and the
# per-analysis inline filters. compute_keep_mask() turns a filter config into a boolean keep-mask
# over the data's rows without touching any widget, so it can run in either context.

import operator
import re

import pandas as pd

from src.side_area_panel.iispwac.iispwac_column_filter import EMPTY_SENTINEL

_NUMERIC_OPS = {
    "<": operator.lt,
    ">": operator.gt,
    "<=": operator.le,
    ">=": operator.ge,
}

# alert kinds returned alongside the mask so the Filter module can highlight the right widget.
ALERT_NONE = None
ALERT_COLUMN = "column"  # no column selected
ALERT_VALUE = "value"  # a numeric comparison needs a numeric value


def empty_mask(series: pd.Series) -> pd.Series:
    """True where the cell is missing or blank -- captures both NaN and empty strings ""."""
    return series.isna() | (series.astype(str).str.strip() == "")


def filter_target_column(config):
    """The single column a filter config targets, or None when none is selected."""
    selected = config.column_selector[0] if config.column_selector else []
    return selected[0] if selected else None


def compute_keep_mask(data, config):
    """Return (mask, error_message, alert_kind) for the given filter config over `data`.

    mask is a boolean pandas Series over the rows to KEEP, or None meaning "keep everything"
    (an unconfigured / no-op filter). error_message is a user-facing string or "". alert_kind is
    one of ALERT_* so a caller with widgets can flag the offending one."""
    selected = config.column_selector[0] if config.column_selector else None
    if not selected:
        return None, "Select a column to filter.", ALERT_COLUMN
    column_name = selected[0]
    if column_name not in data.column_names():
        return None, "", ALERT_NONE  # broken column: handled as broken upstream, no-op here

    spec = config.column_filter
    if spec is None or spec.get("column") != column_name:
        return None, "", ALERT_NONE  # not configured for the current column yet -> no-op

    series = data[column_name].data_series
    mode = spec.get("mode")

    if mode == "numeric":
        operation = spec.get("operation")
        if operation in ("is empty", "is not empty"):
            empties = empty_mask(series)
            mask = empties if operation == "is empty" else ~empties
        else:
            value_text = spec.get("value")
            if value_text in (None, ""):
                return None, "", ALERT_NONE
            numeric = pd.to_numeric(series, errors="coerce")
            if operation in ("==", "!="):
                # Multiple values (space/comma/semicolon separated) -> in / not in. Numeric tokens
                # match numerically; a non-numeric token (e.g. a string ID) falls back to strings.
                tokens = [tok for tok in re.split(r"[,;\s]+", value_text.strip()) if tok != ""]
                if not tokens:
                    return None, "", ALERT_NONE
                try:
                    values = [float(tok) for tok in tokens]
                    is_in = numeric.isin(values)
                except ValueError:
                    is_in = series.astype(str).str.strip().isin(tokens)
                mask = is_in if operation == "==" else ~is_in
            else:
                op = _NUMERIC_OPS.get(operation)
                if op is None:
                    return None, "", ALERT_NONE
                try:
                    value = float(value_text)
                except (TypeError, ValueError):
                    return None, "Enter a numeric value for this comparison.", ALERT_VALUE
                mask = op(numeric, value).fillna(False)
    elif mode == "categorical":
        kept = spec.get("kept_values")
        if kept is None:
            return None, "", ALERT_NONE  # all values kept -> no-op
        # The "(empty)" pseudo-value keeps missing/blank cells; real values match directly.
        keep_empty = EMPTY_SENTINEL in kept
        real_kept = [v for v in kept if v != EMPTY_SENTINEL]
        mask = series.isin(real_kept)
        if keep_empty:
            mask = mask | empty_mask(series)
    else:
        return None, "", ALERT_NONE

    return mask.astype(bool), "", ALERT_NONE


def removed_positions(mask) -> list:
    """Row positions (0-based, in the unfiltered order) that a keep-mask removes."""
    if mask is None:
        return []
    return [i for i, keep in enumerate(mask.tolist()) if not keep]


def apply_mask(data, mask):
    """A copy of `data` keeping only the rows where mask is True (mask None keeps everything)."""
    new_data = data.copy()
    if mask is None:
        return new_data
    for column in new_data.columns:
        column.data_series = column.data_series[mask]
    return new_data
