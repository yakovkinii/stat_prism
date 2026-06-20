#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import pandas as pd

from src.common.constant import ColumnType
from src.common.decorators import log_function
from src.data.data import DataColumn
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.utility import unique_name
from src.side_area_panel.modules.dp_onehot.dp_onehot_result import OneHotResult
from src.side_area_panel.modules.dp_onehot.dp_onehot_ui import Elements


@log_function
def dp_onehot_main(elements: Elements, result: OneHotResult, update):
    cfg = result.config
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    new_data = data.copy()
    # Default to a pass-through so downstream stays valid while inputs are incomplete.
    result.data = new_data

    selected = cfg.column_selector[0] if cfg.column_selector else None
    if not selected:
        elements.column_selector.set_alert(0)
        return result
    column_name = selected[0]
    if column_name not in new_data.column_names():
        elements.column_selector.set_alert(0)
        return result

    source = new_data[column_name]
    series = source.data_series
    # Categories in the column's defined order (alphabetical fallback via ordered_categories).
    present = list(series.dropna().astype(str).unique())
    categories = new_data.ordered_categories(column_name, present)
    if not categories:
        return result  # nothing to encode -> pass-through

    drop = cfg.drop_reference if cfg.drop_reference is not None else True
    if drop:
        ref = (cfg.reference or "").strip()
        reference = ref if ref in categories else categories[0]
        categories = [c for c in categories if c != reference]

    str_series = series.apply(lambda v: v if pd.isna(v) else str(v))
    anchor = column_name
    for category in categories:
        target = unique_name(f"{column_name} = {category}", set(new_data.column_names()))
        indicator = pd.Series(
            [1 if (not pd.isna(v) and v == category) else 0 for v in str_series.tolist()],
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
