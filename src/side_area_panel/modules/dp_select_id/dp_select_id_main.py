#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from src.common.constant import ColumnType, ID_COLUMN_NAME
from src.common.decorators import log_function
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.dp_select_id.dp_select_id_result import SelectIDResult
from src.side_area_panel.modules.dp_select_id.dp_select_id_ui import Elements


@log_function
def dp_select_id_main(elements: Elements, result: SelectIDResult, update):
    cfg = result.config
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    new_data = data.copy()
    # Default to a pass-through so downstream stays valid while inputs are incomplete/invalid.
    result.data = new_data

    selected = cfg.column_selector[0] if cfg.column_selector else None
    if not selected:
        elements.column_selector.set_alert(0)
        return result
    column_name = selected[0]

    series = new_data[column_name].data_series
    # A valid identifier has no missing values and only unique values.
    if series.isna().any() or series.duplicated().any():
        elements.column_selector.set_alert(0)
        return result

    # Drop the previous ID column(s) before promoting the new one (frees the "ID" name).
    for name in list(new_data.column_names()):
        if new_data[name].column_type == ColumnType.ID:
            new_data.remove_column(name)

    id_column = new_data[column_name]
    new_data.rename_column(column_name, ID_COLUMN_NAME)
    id_column.column_type = ColumnType.ID
    id_column.is_numeric = False
    id_column.order = {}

    # Move the promoted column to the first position.
    new_data.remove_column(ID_COLUMN_NAME)
    new_data.add_column_first(id_column)

    result.data = new_data
    return result
