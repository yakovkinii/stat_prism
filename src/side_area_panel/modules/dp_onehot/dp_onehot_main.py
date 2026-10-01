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
from src.data.data import DataColumn, category_display_series
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.utility import unique_name
from src.side_area_panel.modules.dp_onehot.dp_onehot_result import OneHotResult
from src.side_area_panel.modules.dp_onehot.dp_onehot_ui import Elements


def _dedupe(values):
    out = []
    seen = set()
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        out.append(value)
    return out


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
    result.error_message = ""

    selected = cfg.column_selector[0] if cfg.column_selector else None
    if not selected:
        elements.column_selector.set_alert(0)
        result.error_message = "Select a column to encode."
        return result
    column_name = selected[0]
    if column_name not in new_data.column_names():
        elements.column_selector.set_alert(0)
        result.error_message = "Select a column to encode."
        return result

    source = new_data[column_name]
    series = source.data_series
    # Categories in the column's defined order first; convert to stable display strings only after
    # ordering so numeric/custom order keys still match. Missing values are encoded as an mdash
    # category rather than relying on pandas' assorted string forms for NA/NaN.
    present = list(series.unique())
    categories = _dedupe(new_data.ordered_category_labels(column_name, present))
    if not categories:
        return result  # nothing to encode -> pass-through

    drop = cfg.drop_reference if cfg.drop_reference is not None else False
    if drop:
        ref = (cfg.reference or "").strip()
        reference = ref if ref in categories else categories[0]
        categories = [c for c in categories if c != reference]

    str_series = category_display_series(series)
    anchor = column_name
    for category in categories:
        target = unique_name(f"{column_name} = {category}", set(new_data.column_names()))
        indicator = pd.Series(
            [1 if v == category else 0 for v in str_series.tolist()],
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
