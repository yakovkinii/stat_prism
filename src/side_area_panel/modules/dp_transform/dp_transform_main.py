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


import pandas as pd

from src.common.constant import ColumnType
from src.common.decorators import log_function
from src.data.data import category_display_value
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.utility import apply_normalization, ordinal_numeric_cast_warning, unique_name
from src.side_area_panel.modules.dp_transform.dp_transform_result import TransformResult
from src.side_area_panel.modules.dp_transform.dp_transform_ui import Elements


def _parse_float(text):
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def _normalized_mapping(spec):
    return {category_display_value(source): target for source, target in (spec.get("mapping") or [])}


def _mapped_value(value, mapping):
    return mapping.get(category_display_value(value), value)


def _mapped_series(column, spec):
    series = column.data_series
    mapping = _normalized_mapping(spec)
    if mapping:
        series = series.map(lambda v: _mapped_value(v, mapping))
    return series


def _non_empty(series):
    return series.notna() & (series.astype(str).str.strip() != "")


def _restore_flipped_face_dtype(column, flipped):
    if column.column_dtype == "str":
        return flipped.map(lambda v: v if pd.isna(v) else str(int(v) if float(v).is_integer() else v)), "str"
    if column.column_dtype == "int" and flipped.notna().all() and bool((flipped == flipped.round()).all()):
        return flipped.astype("int64"), "int"
    return flipped, "float"


def _remap_prescribed_order(order, mapping):
    if not order:
        return {}
    remapped = {}
    for raw, _rank in sorted(order.items(), key=lambda item: item[1]):
        value = _mapped_value(raw, mapping)
        value = value if pd.isna(value) else str(value)
        if value not in remapped:
            remapped[value] = len(remapped) + 1
    return remapped


def _flip_target_type(column, spec):
    try:
        return ColumnType(spec.get("type"))
    except (ValueError, TypeError):
        return column.column_type


def _flip_casts_ordinal(column, spec) -> bool:
    """True when the flip will treat an ordinal source column as numeric (its face values are used),
    so the caller can raise the 'treated as numeric' warning -- as Invert Scale / Calculate Scale do."""
    return (
        column.column_type == ColumnType.ORDINAL
        and _flip_target_type(column, spec) == ColumnType.ORDINAL
        and bool(spec.get("flip"))
    )


def _ordinal_flip_error(column, spec):
    if _flip_target_type(column, spec) != ColumnType.ORDINAL or not spec.get("flip"):
        return None
    if spec.get("order"):
        return f"Cannot flip '{column.column_name}' after assigning an explicit ordinal order."
    if column.column_type == ColumnType.ORDINAL and column.order:
        return f"Cannot flip ordinal column '{column.column_name}' because it has a prescribed order."
    series = _mapped_series(column, spec)
    numeric = pd.to_numeric(series, errors="coerce")
    if bool((numeric.isna() & _non_empty(series)).any()):
        return f"Cannot flip '{column.column_name}' because its ordinal face values are not numeric."
    return None


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
    result.warnings = []

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
    for column_name in valid:
        error = _ordinal_flip_error(data[column_name], spec)
        if error:
            elements.column_selector.set_alert(0)
            result.error_message = error
            return result

    # Flipping an ordinal uses its numeric face values -> warn (consistent with Invert / Calculate
    # Scale, the other modules that treat ordinals as numeric).
    cast_ordinals = [c for c in valid if _flip_casts_ordinal(data[c], spec)]
    if cast_ordinals:
        result.set_warning(ordinal_numeric_cast_warning(cast_ordinals))

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
    mapping = _normalized_mapping(spec)
    col.data_series = _mapped_series(col, spec)

    # 2. Target type.
    try:
        ctype = ColumnType(spec.get("type"))
    except (ValueError, TypeError):
        ctype = col.column_type
    col.column_type = ctype
    col.is_numeric = ctype == ColumnType.NUMERIC

    # Ordinal flip is allowed only for plain numeric face-value scales. Validation above rejects
    # explicit/custom ordinal orders and non-numeric face values, so this never uses order codes.
    flipped_ordinal = False
    if ctype == ColumnType.ORDINAL and spec.get("flip"):
        numeric = pd.to_numeric(col.data_series, errors="coerce")
        if not numeric.dropna().empty:
            reference = _parse_float(spec.get("flip_reference"))
            if reference is None:
                reference = numeric.max() + numeric.min()
            col.data_series, col.column_dtype = _restore_flipped_face_dtype(col, reference - numeric)
            col.order = {}
            flipped_ordinal = True

    if ctype == ColumnType.NUMERIC:
        coerced = pd.to_numeric(col.data_series, errors="coerce")
        method = spec.get("normalize") or "None"
        if method != "None":
            coerced = apply_normalization(coerced, method)
        if coerced.notna().all() and bool((coerced == coerced.round()).all()):
            col.data_series = coerced.astype("int64")
            col.column_dtype = "int"
        else:
            col.data_series = coerced
            col.column_dtype = "float"
    elif not flipped_ordinal:
        # nominal / ordinal -> string labels (keep NaN as NaN)
        col.data_series = col.data_series.apply(lambda v: v if pd.isna(v) else str(v))
        col.column_dtype = "str"

    # 3. Ordering (ordinal / nominal); explicit order expressed over the mapped values.
    if ctype in (ColumnType.ORDINAL, ColumnType.NOMINAL):
        # Only (re)build the order from an explicit one; otherwise keep the upstream order
        # (automatically_update_order fills only the values that lack a position). See the same
        # note in dp_preprocess_main.
        if spec.get("order"):
            col.order = {}
            for raw in spec["order"]:
                value = _mapped_value(raw, mapping)
                value = value if pd.isna(value) else str(value)
                if value not in col.order:
                    col.order[value] = len(col.order) + 1
        elif not flipped_ordinal and (mapping or col.order):
            col.order = _remap_prescribed_order(col.order, mapping)
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
