#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import pandas as pd

from src.common.constant import ColumnType
from src.common.decorators import log_function
from src.data.data import DataColumn
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.utility import unique_name
from src.side_area_panel.modules.dp_split_multiselect.dp_split_multiselect_result import SplitMultiSelectResult
from src.side_area_panel.modules.dp_split_multiselect.dp_split_multiselect_ui import Elements


def _split_cell(value, delimiter):
    """The set of non-empty, stripped options in one cell (empty for missing/blank)."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    return [token.strip() for token in str(value).split(delimiter) if token.strip() != ""]


@log_function
def dp_split_multiselect_main(elements: Elements, result: SplitMultiSelectResult, update):
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
        result.error_message = "Select a column to split."
        return result
    column_name = selected[0]
    if column_name not in new_data.column_names():
        elements.column_selector.set_alert(0)
        result.error_message = "Select a column to split."
        return result

    delimiter = (cfg.delimiter or ",").strip() or ","
    prefix = (cfg.prefix or "").strip()
    source = new_data[column_name]

    # Per-row option sets, and the distinct options in first-seen order.
    row_options = [_split_cell(v, delimiter) for v in source.data_series.tolist()]
    options = []
    seen = set()
    for opts in row_options:
        for opt in opts:
            if opt not in seen:
                seen.add(opt)
                options.append(opt)

    if not options:
        return result  # nothing to split (e.g. all blank) -> pass-through

    # One 0/1 indicator column per option, inserted in order right after the source.
    anchor = column_name
    for option in options:
        target = unique_name(f"{prefix}{option}" if prefix else option, set(new_data.column_names()))
        indicator = pd.Series(
            [1 if option in opts else 0 for opts in row_options],
            name=target,
            dtype="int64",
        )
        new_col = DataColumn.initialize_from_series(indicator)
        new_col.column_type = ColumnType.NUMERIC
        new_col.is_numeric = True
        new_col.column_dtype = "int"
        new_col.color = source.color
        new_data.add_column_after(anchor, new_col)
        anchor = target

    new_data.update_lookups()
    result.data = new_data
    return result
