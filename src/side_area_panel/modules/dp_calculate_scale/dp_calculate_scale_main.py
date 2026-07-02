#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import pandas as pd

from src.common.decorators import log_function
from src.data.data import DataColumn
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.utility import to_stanine, unique_name
from src.side_area_panel.modules.dp_calculate_scale.dp_calculate_scale_result import CalculateScaleResult
from src.side_area_panel.modules.dp_calculate_scale.dp_calculate_scale_ui import Elements


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

    question_columns = cfg.column_selector[0] or []
    # Optional reverse-keyed items (second selector field); flipped first, then pooled in.
    flipped_columns = (cfg.column_selector[1] if len(cfg.column_selector) > 1 else None) or []
    all_item_columns = list(question_columns) + list(flipped_columns)
    if not all_item_columns:
        elements.column_selector.set_alert(0)
        result.error_message = "Select at least one item column."
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

    # Reference for reverse-scoring: manual override, else (max + min) over the pooled values
    # of the reverse-keyed columns (same rule as the Invert Scale module).
    flip_reference = cfg.flip_reference
    if flipped_columns and flip_reference is None:
        pooled = pd.concat(
            [pd.to_numeric(data[column].data_series, errors="coerce") for column in flipped_columns],
            ignore_index=True,
        )
        if not pooled.dropna().empty:
            flip_reference = pooled.max() + pooled.min()

    def _flip(series):
        return flip_reference - series if flip_reference is not None else series

    # Build an aligned numeric frame of all items (raw questions + reverse-scored columns).
    item_series = [pd.to_numeric(data[column].data_series, errors="coerce") for column in question_columns]
    item_series += [_flip(pd.to_numeric(data[column].data_series, errors="coerce")) for column in flipped_columns]
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

    if cfg.scale == "Stanine":
        scale_series = to_stanine(scale_series)
    elif cfg.scale not in [None, "None"]:
        raise ValueError(f"Unknown normalization option: {cfg.scale}")

    scale_series.name = scale_name
    new_column = DataColumn.initialize_from_series(scale_series)
    new_column.color = cfg.color  # user-chosen colour tag for the new scale column

    data.add_column_after(all_item_columns[-1], new_column)

    # Reverse-scored source columns: when "Replace" is on (default), write the flipped values
    # back into those columns in the output so they match what went into the scale. (Skipped
    # for Delete, where the columns are removed anyway.)
    replace_flipped = cfg.replace_flipped if cfg.replace_flipped is not None else True
    action = cfg.questions_action or "Keep"
    if flipped_columns and replace_flipped and flip_reference is not None and action != "Delete":
        for column in flipped_columns:
            source = data[column]
            source.data_series = _flip(pd.to_numeric(source.data_series, errors="coerce"))
            source.order = {}
            source.automatically_update_order()

    # Decide what happens to the item columns the scale was built from.
    if action == "Delete":
        for column in all_item_columns:
            data.remove_column(column)
    elif action == "Auto-rename":
        # Auto-rename already gives a fresh "<scale> Q{i}" name, so no "(flipped)" suffix.
        for i, column in enumerate(all_item_columns, start=1):
            data[column].color = cfg.questions_color  # tag before rename (column object persists)
            target = f"{scale_name} Q{i}"
            if target != column:
                target = unique_name(target, set(data.column_names()) - {column})
                data.rename_column(column, target)
    elif action == "Keep":
        for column in question_columns:
            data[column].color = cfg.questions_color
        for column in flipped_columns:
            data[column].color = cfg.questions_color
            # Mark a replaced reverse-scored column as flipped in its name.
            if replace_flipped and flip_reference is not None:
                new_name = unique_name(f"{column} (flipped)", set(data.column_names()) - {column})
                data.rename_column(column, new_name)
    else:
        raise ValueError(f"Unknown questions action: {action}")

    result.data = data.copy()
    return result
