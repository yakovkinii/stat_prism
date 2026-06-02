#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import pandas as pd

from src.common.decorators import log_function
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.utility import to_stanine
from src.side_area_panel.modules.dp_process_column.dp_process_column_result import (
    ProcessColumnResult,
)
from src.side_area_panel.modules.dp_process_column.dp_process_column_ui import Elements


@log_function
def dp_process_column_main(elements: Elements, result: ProcessColumnResult):
    cfg = result.config
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    result.data = data.copy()

    if cfg.column_selector[0] in [None, []]:
        elements.column_selector.set_alert(0)
        return result

    original_column_name = cfg.column_selector[0][0]
    column = data[original_column_name].copy()
    new_name = cfg.rename['new_name'] if cfg.rename['rename'] else original_column_name

    if new_name != original_column_name and new_name in data.column_names():
        # A renamed column cannot collide with another existing column.
        elements.rename.set_alert()
        return result

    keep_original = cfg.keep_original
    if keep_original and (new_name == original_column_name or cfg.rename['rename'] is False):
        elements.rename.set_alert()
        elements.keep_original.set_alert()
        return result

    column.rename(new_name)

    if not keep_original:
        data.replace_column(original_column_name, column)
    else:
        data.add_column_after(original_column_name, column)

    if cfg.flip['flip']:
        reference = cfg.flip.get('reference_value')
        if reference is None:
            # Auto: reference = max + min of the column.
            numeric = pd.to_numeric(column.data_series, errors="coerce")
            reference = numeric.max() + numeric.min()
        column.data_series = reference - column.data_series

    if cfg.scale == "Stanine":
        column.data_series = to_stanine(column.data_series)
    elif cfg.scale in [None, "None"]:
        pass
    else:
        raise ValueError(f"Unknown normalization option: {cfg.scale}")

    result.data = data.copy()
    return result
