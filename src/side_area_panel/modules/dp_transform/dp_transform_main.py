#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import numpy as np
import pandas as pd

from src.common.constant import ColumnType
from src.common.decorators import log_function
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.utility import to_stanine, unique_name
from src.side_area_panel.modules.dp_transform.dp_transform_result import TransformResult
from src.side_area_panel.modules.dp_transform.dp_transform_ui import Elements


def _parse_float(text):
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def _apply_normalize(x: pd.Series, method: str) -> pd.Series:
    if method == "Z-score":
        std = x.std()
        return (x - x.mean()) / std if std else x - x.mean()
    if method == "Center":
        return x - x.mean()
    if method == "Min-max":
        span = x.max() - x.min()
        return (x - x.min()) / span if span else x - x.min()
    if method == "Log":
        return np.log(x.where(x > 0))
    if method == "Rank":
        return x.rank(method="average")
    if method == "Stanine":
        return to_stanine(x)
    return x


@log_function
def dp_transform_main(elements: Elements, result: TransformResult, update):
    cfg = result.config
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    new_data = data.copy()
    # Default to a pass-through so downstream stays valid while inputs are incomplete.
    result.data = new_data
    result.error_message = ""

    selected = cfg.column_selector[0] if cfg.column_selector else None
    if not selected:
        elements.column_selector.set_alert(0)
        result.error_message = "Select at least one column."
        return result

    valid = [c for c in selected if c in new_data.column_names()]
    if not valid:
        elements.column_selector.set_alert(0)
        result.error_message = "Selected column(s) not available."
        return result

    spec = cfg.transform_spec if isinstance(cfg.transform_spec, dict) else {}
    # The same spec is applied to every selected column; renaming only makes sense for one.
    single = len(valid) == 1
    for column_name in valid:
        _transform_column(new_data, column_name, spec, rename=single)

    new_data.update_lookups()
    result.data = new_data
    return result


def _transform_column(new_data, column_name, spec, rename):
    col = new_data[column_name]

    # 1. Value mapping (keys are original values; unmapped values pass through).
    mapping = {f: t for f, t in (spec.get("mapping") or [])}
    if mapping:
        col.data_series = col.data_series.map(lambda v: mapping[v] if v in mapping else v)

    # 2. Target type.
    try:
        ctype = ColumnType(spec.get("type"))
    except (ValueError, TypeError):
        ctype = col.column_type
    col.column_type = ctype
    col.is_numeric = ctype == ColumnType.NUMERIC

    # Ordinal flip works on the numeric codes, before any stringification.
    if ctype == ColumnType.ORDINAL and spec.get("flip"):
        numeric = pd.to_numeric(col.data_series, errors="coerce")
        if not numeric.dropna().empty:
            reference = _parse_float(spec.get("flip_reference"))
            if reference is None:
                reference = numeric.max() + numeric.min()
            col.data_series = reference - numeric

    if ctype == ColumnType.NUMERIC:
        coerced = pd.to_numeric(col.data_series, errors="coerce")
        method = spec.get("normalize") or "None"
        if method != "None":
            coerced = _apply_normalize(coerced, method)
        if coerced.notna().all() and bool((coerced == coerced.round()).all()):
            col.data_series = coerced.astype("int64")
            col.column_dtype = "int"
        else:
            col.data_series = coerced
            col.column_dtype = "float"
    else:
        # nominal / ordinal -> string labels (keep NaN as NaN)
        col.data_series = col.data_series.apply(lambda v: v if pd.isna(v) else str(v))
        col.column_dtype = "str"

    # 3. Ordering (ordinal only); explicit order expressed over the mapped values.
    if ctype == ColumnType.ORDINAL:
        col.order = {}
        for raw in (spec.get("order") or []):
            value = mapping.get(raw, raw)
            value = value if pd.isna(value) else str(value)
            if value not in col.order:
                col.order[value] = len(col.order) + 1
        col.automatically_update_order()
    else:
        col.order = {}

    # 4. Rename (single-column only; replace in place, kept unique against other columns).
    if rename:
        target = (spec.get("new_name") or "").strip() or column_name
        others = set(new_data.column_names()) - {column_name}
        if target in others:
            target = unique_name(target, others)
        if target != column_name:
            col.rename(target)

    # 5. Colour tag.
    col.color = spec.get("color")
