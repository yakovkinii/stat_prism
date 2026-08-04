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


from src.common.constant import ID_COLUMN_NAME, ColumnType
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
    result.error_message = ""

    selected = cfg.column_selector[0] if cfg.column_selector else None
    if not selected:
        elements.column_selector.set_alert(0)
        result.error_message = "Select an ID column."
        return result
    column_name = selected[0]

    series = new_data[column_name].data_series
    # A valid identifier has no missing values and only unique values.
    if series.isna().any() or series.duplicated().any():
        elements.column_selector.set_alert(0)
        result.error_message = "ID column must have unique, non-missing values."
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
