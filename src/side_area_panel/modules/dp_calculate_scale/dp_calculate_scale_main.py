#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import pandas as pd

from src.common.decorators import log_function
from src.data.data import DataColumn
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.utility import to_stanine, unique_name
from src.side_area_panel.modules.dp_calculate_scale.dp_calculate_scale_result import (
    CalculateScaleResult,
)
from src.side_area_panel.modules.dp_calculate_scale.dp_calculate_scale_ui import Elements


@log_function
def dp_calculate_scale_main(elements: Elements, result: CalculateScaleResult):
    cfg = result.config
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    # Default to a pass-through so downstream stays valid while inputs are incomplete.
    result.data = data.copy()

    question_columns = cfg.column_selector[0]
    if question_columns in [None, []]:
        elements.column_selector.set_alert(0)
        return result

    scale_name = (cfg.name or "").strip()
    if scale_name == "":
        elements.name.set_alert()
        return result
    if scale_name in data.column_names():
        # A new column cannot reuse an existing name.
        elements.name.set_alert()
        return result

    # Build an aligned numeric frame of the selected questions (raw series, no row reordering).
    items = pd.concat(
        [pd.to_numeric(data[column].data_series, errors="coerce") for column in question_columns],
        axis=1,
    )

    method = cfg.method or "Sum"
    if method == "Sum":
        scale_series = items.sum(axis=1, min_count=1)
    elif method == "Mean":
        scale_series = items.mean(axis=1)
    else:
        raise ValueError(f"Unknown aggregation method: {method}")

    if cfg.scale == "Stanine":
        scale_series = to_stanine(scale_series)
    elif cfg.scale not in [None, "None"]:
        raise ValueError(f"Unknown normalization option: {cfg.scale}")

    scale_series.name = scale_name
    new_column = DataColumn.initialize_from_series(scale_series)

    data.add_column_after(question_columns[-1], new_column)

    # Decide what happens to the question columns the scale was built from.
    action = cfg.questions_action or "Keep"
    if action == "Delete":
        for column in question_columns:
            data.remove_column(column)
    elif action == "Auto-rename":
        for i, column in enumerate(question_columns, start=1):
            target = f"{scale_name} Q{i}"
            if target != column:
                target = unique_name(target, set(data.column_names()) - {column})
                data.rename_column(column, target)
    elif action != "Keep":
        raise ValueError(f"Unknown questions action: {action}")

    result.data = data.copy()
    return result
