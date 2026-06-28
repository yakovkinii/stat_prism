#  Copyright (c) 2023 StatPrism Team. All rights reserved.
"""Detection logic for the Response Quality cleaning step.

Each check takes a ``Data`` plus the selected question columns and returns an *ordered list
of candidate respondent IDs* proposed for removal -- the same contract the outlier detectors
use, so the shared Remove-list element and ``finalize_removal`` apply unchanged.

The percentage-based checks share one ``min_pct`` knob ("flag at this share of the items"),
so a single threshold control in the panel drives them all consistently.
"""

import math

import pandas as pd

from src.side_area_panel.modules.common.removal import ids_for_mask

CHECK_DUPLICATES = "Duplicate entries"
CHECK_LONGSTRING = "Long string"
CHECK_MISSING = "High missingness"
CHECK_LOWVAR = "Low variability"

# Long string leads the list so it is the default check (the most common careless-response screen).
CHECKS = [CHECK_LONGSTRING, CHECK_DUPLICATES, CHECK_MISSING, CHECK_LOWVAR]

_SENTINEL = object()


def _frame(data, columns):
    cols = [c for c in (columns or []) if c in data.column_names()]
    if not cols:
        return None
    return pd.concat([data.get_series(column=c, map_ordinal=True) for c in cols], axis=1)


def _longest_run(values) -> int:
    """Longest run of identical *consecutive* answers; missing values break runs."""
    best = current = 0
    prev = _SENTINEL
    for value in values:
        if pd.isna(value):
            prev = _SENTINEL
            current = 0
            continue
        if value == prev:
            current += 1
        else:
            prev = value
            current = 1
        if current > best:
            best = current
    return best


def detect_duplicates(data, columns) -> list:
    """Rows that repeat an earlier row across the selected columns (first kept)."""
    frame = _frame(data, columns)
    if frame is None:
        return []
    return ids_for_mask(data, frame.duplicated(keep="first"))


def detect_longstring(data, columns, min_pct) -> list:
    """Respondents whose longest identical consecutive run covers >= min_pct% of items."""
    frame = _frame(data, columns)
    if frame is None or frame.shape[1] < 2:
        return []
    need = max(2, math.ceil(min_pct / 100 * frame.shape[1]))
    runs = frame.apply(lambda row: _longest_run(row.tolist()), axis=1)
    return ids_for_mask(data, runs >= need)


def detect_low_variability(data, columns, min_pct) -> list:
    """Respondents whose single most-common answer covers >= min_pct% of items (little
    variation across questions), regardless of order."""
    frame = _frame(data, columns)
    if frame is None or frame.shape[1] < 2:
        return []
    need = max(2, math.ceil(min_pct / 100 * frame.shape[1]))

    def modal_count(row):
        present = row.dropna()
        if present.empty:
            return 0
        return int(present.value_counts().iloc[0])

    counts = frame.apply(modal_count, axis=1)
    return ids_for_mask(data, counts >= need)


def detect_high_missing(data, columns, min_pct) -> list:
    """Respondents who left >= min_pct% of the selected items blank."""
    frame = _frame(data, columns)
    if frame is None:
        return []
    need = max(1, math.ceil(min_pct / 100 * frame.shape[1]))
    missing = frame.isna().sum(axis=1)
    return ids_for_mask(data, missing >= need)


def detect_response_quality(data, check, columns, min_pct) -> list:
    if check == CHECK_DUPLICATES:
        return detect_duplicates(data, columns)
    if check == CHECK_LONGSTRING:
        return detect_longstring(data, columns, min_pct)
    if check == CHECK_MISSING:
        return detect_high_missing(data, columns, min_pct)
    if check == CHECK_LOWVAR:
        return detect_low_variability(data, columns, min_pct)
    return []
