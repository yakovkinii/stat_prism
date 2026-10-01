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
from src.data.data import DataColumn
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.utility import (
    apply_normalization,
    ordinal_numeric_cast_warning,
    smart_comma_join,
    unique_name,
)
from src.side_area_panel.modules.dp_calculate_scale.dp_calculate_scale_result import CalculateScaleResult
from src.side_area_panel.modules.dp_calculate_scale.dp_calculate_scale_ui import Elements

_ITEM_TYPES = (ColumnType.NUMERIC, ColumnType.ORDINAL)


def _face_value_numeric(data, column_name):
    """Numeric item values for Calculate Scale.

    Ordinal columns are deliberately parsed from their displayed values, not from their internal
    order codes. Empty strings / missing values become NaN and are handled by the missing-value
    policy; non-empty, non-numeric labels are reported as invalid input.
    """
    series = data[column_name].data_series
    numeric = pd.to_numeric(series, errors="coerce")
    non_empty = series.notna() & (series.astype(str).str.strip() != "")
    if bool((numeric.isna() & non_empty).any()):
        return numeric, False
    return numeric, True


def _restore_flipped_face_dtype(column, flipped):
    """Store a flipped source column on its face-value scale, preserving ordinal columns as ordinal."""
    if column.column_dtype == "str":
        return flipped.map(lambda v: v if pd.isna(v) else str(int(v) if float(v).is_integer() else v)), "str"
    if column.column_dtype == "int" and flipped.notna().all() and bool((flipped == flipped.round()).all()):
        return flipped.astype("int64"), "int"
    return flipped, "float"


@log_function
def dp_calculate_scale_main(elements: Elements, result: CalculateScaleResult, update):
    cfg = result.config
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    # Default to a pass-through so downstream stays valid while inputs are incomplete.
    result.data = data.copy()
    result.error_message = ""
    result.warnings = []

    question_columns = cfg.column_selector[0] or []
    # Optional reverse-keyed items (second selector field); flipped first, then pooled in.
    flipped_columns = (cfg.column_selector[1] if len(cfg.column_selector) > 1 else None) or []
    all_item_columns = list(question_columns) + list(flipped_columns)
    if not all_item_columns:
        elements.column_selector.set_alert(0)
        result.error_message = "Select at least one item column."
        return result

    available = set(data.column_names())
    invalid_type = [
        column for column in all_item_columns if column not in available or data[column].column_type not in _ITEM_TYPES
    ]
    if invalid_type:
        elements.column_selector.set_alert(0)
        result.error_message = "Calculate Scale accepts numeric or ordinal item columns only."
        return result

    item_values = {}
    invalid_values = []
    for column in all_item_columns:
        item_values[column], valid = _face_value_numeric(data, column)
        if not valid:
            invalid_values.append(column)
    if invalid_values:
        elements.column_selector.set_alert(0)
        result.error_message = "Ordinal item values must be parseable as numbers: " + ", ".join(invalid_values)
        return result

    # Reverse-keying is an inversion done on face values, so it is only well-defined for an ordinal with
    # no prescribed order (its face values are already validated numeric above); refuse a flipped
    # ordinal that carries a custom order.
    bad_flip = [c for c in flipped_columns if data[c].column_type == ColumnType.ORDINAL and data[c].order]
    if bad_flip:
        elements.column_selector.set_alert(1)
        result.error_message = (
            "Cannot reverse-key ordinal column(s) with a prescribed order: "
            + smart_comma_join([str(c) for c in bad_flip])
            + ". Reverse only ordinals with no custom order."
        )
        return result

    scale_name = (cfg.name or "").strip()
    if scale_name == "":
        elements.name.set_alert()
        result.error_message = "Enter a name for the scale."
        return result
    if scale_name in data.column_names():
        # A new column cannot reuse an existing name.
        elements.name.set_alert()
        result.error_message = f"A column named '{scale_name}' already exists."
        return result

    # Ordinal items are combined using their numeric face values -> warn (consistent with the other
    # modules that treat ordinals as numeric).
    cast_ordinals = [c for c in all_item_columns if data[c].column_type == ColumnType.ORDINAL]
    if cast_ordinals:
        result.set_warning(ordinal_numeric_cast_warning(cast_ordinals))

    # Reference for reverse-scoring: manual override, else (max + min) over the pooled values
    # of the reverse-keyed columns (same rule as the Invert Scale module).
    flip_reference = cfg.flip_reference
    if flipped_columns and flip_reference is None:
        pooled = pd.concat([item_values[column] for column in flipped_columns], ignore_index=True)
        if not pooled.dropna().empty:
            flip_reference = pooled.max() + pooled.min()

    def _flip(series):
        return flip_reference - series if flip_reference is not None else series

    # Build an aligned numeric frame of all items (raw questions + reverse-scored columns).
    item_series = [item_values[column] for column in question_columns]
    item_series += [_flip(item_values[column]) for column in flipped_columns]
    items = pd.concat(item_series, axis=1)

    # Missing-value policy:
    #  * "Skip respondent": any missing item -> no scale value for that row.
    #  * "Allow up to max %": aggregate over the present items for rows whose share
    #    of missing items is within the threshold; other rows get no scale value.
    n_items = items.shape[1]
    missing_fraction = items.isna().sum(axis=1) / n_items
    missing_mode = cfg.missing_values or "Skip respondent"
    threshold = cfg.missing_threshold if cfg.missing_threshold is not None else 0
    if missing_mode == "Skip respondent":
        allow = missing_fraction == 0
    else:
        allow = (missing_fraction * 100) <= threshold

    method = cfg.method or "Sum"
    if method == "Sum":
        aggregated = items.sum(axis=1, min_count=1)  # NaN when no items present
    elif method == "Mean":
        aggregated = items.mean(axis=1)  # skips missing items
    else:
        raise ValueError(f"Unknown aggregation method: {method}")
    scale_series = aggregated.where(allow)

    if cfg.scale and cfg.scale != "None":
        scale_series = apply_normalization(scale_series, cfg.scale)

    scale_series.name = scale_name
    new_column = DataColumn.initialize_from_series(scale_series)
    # A blank (transparent) color means "no color tag" for the new column; keep it untagged.
    if cfg.color:
        new_column.color = cfg.color

    # Insert the scale after the right-most of its item columns (by position in the data), so it
    # lands after all of them rather than in the middle when reverse-scored items sit earlier.
    names = data.column_names()
    last_item = max(all_item_columns, key=names.index)
    data.add_column_after(last_item, new_column)

    # Reverse-scored source columns: when "Replace" is on (default), write the flipped values
    # back into those columns in the output so they match what went into the scale. (Skipped
    # for Delete, where the columns are removed anyway.)
    replace_flipped = cfg.replace_flipped if cfg.replace_flipped is not None else True
    action = cfg.questions_action or "Keep"
    if flipped_columns and replace_flipped and flip_reference is not None and action != "Delete":
        for column in flipped_columns:
            source = data[column]
            source.data_series, source.column_dtype = _restore_flipped_face_dtype(source, _flip(item_values[column]))
            # Reverse-keying an ordinal changes its displayed face values but does not make the
            # source question numeric. With no prescribed order, downstream ordinal analysis infers
            # the new order from those flipped face values.
            source.order = {}
            source.automatically_update_order()

    # Decide what happens to the item columns the scale was built from.
    if action == "Delete":
        for column in all_item_columns:
            data.remove_column(column)
    elif action == "Auto-rename":
        # Auto-rename already gives a fresh "<scale> Q{i}" name, so no "(flipped)" suffix.
        for i, column in enumerate(all_item_columns, start=1):
            if cfg.color:  # a blank (transparent) color leaves the item's existing tag unchanged
                data[column].color = cfg.color  # tag before rename (column object persists)
            target = f"{scale_name} Q{i}"
            if target != column:
                target = unique_name(target, set(data.column_names()) - {column})
                data.rename_column(column, target)
    elif action == "Keep":
        for column in question_columns:
            if cfg.color:
                data[column].color = cfg.color
        for column in flipped_columns:
            if cfg.color:
                data[column].color = cfg.color
            # Mark a replaced reverse-scored column as flipped in its name.
            if replace_flipped and flip_reference is not None:
                new_name = unique_name(f"{column} (flipped)", set(data.column_names()) - {column})
                data.rename_column(column, new_name)
    else:
        raise ValueError(f"Unknown questions action: {action}")

    result.data = data.copy()
    return result
