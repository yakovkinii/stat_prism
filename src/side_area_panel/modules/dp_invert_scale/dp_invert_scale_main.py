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

from src.common.decorators import log_function
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.utility import unique_name
from src.side_area_panel.modules.dp_invert_scale.dp_invert_scale_result import InvertScaleResult
from src.side_area_panel.modules.dp_invert_scale.dp_invert_scale_ui import Elements


@log_function
def dp_invert_scale_main(elements: Elements, result: InvertScaleResult, update):
    cfg = result.config
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    # Default to a pass-through so downstream stays valid while inputs are incomplete.
    result.data = data.copy()
    result.error_message = ""

    columns = cfg.column_selector[0]
    if columns in [None, []]:
        elements.column_selector.set_alert(0)
        result.error_message = "Select at least one column."
        return result

    # All selected columns share one reference. Auto = (max + min) over the pooled
    # values of every selected column; a manual reference overrides it.
    reference = cfg.reference
    if reference is None:
        pooled = pd.concat(
            [pd.to_numeric(data[column].data_series, errors="coerce") for column in columns],
            ignore_index=True,
        )
        if pooled.dropna().empty:
            return result
        reference = pooled.max() + pooled.min()

    existing = set(data.column_names())
    for original_column_name in columns:
        new_name = unique_name(f"{original_column_name} (inverted)", existing)

        inverted = data[original_column_name].copy()
        inverted.data_series = reference - pd.to_numeric(inverted.data_series, errors="coerce")
        inverted.rename(new_name)
        # Rebuild the ordinal/nominal order to reflect the new (inverted) values.
        inverted.order = {}
        inverted.automatically_update_order()

        data.add_column_after(original_column_name, inverted)
        existing.add(new_name)

    result.data = data.copy()
    return result
