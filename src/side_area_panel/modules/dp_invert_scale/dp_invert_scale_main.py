#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import pandas as pd

from src.common.decorators import log_function
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.utility import unique_name
from src.side_area_panel.modules.dp_invert_scale.dp_invert_scale_result import (
    InvertScaleResult,
)
from src.side_area_panel.modules.dp_invert_scale.dp_invert_scale_ui import Elements


@log_function
def dp_invert_scale_main(elements: Elements, result: InvertScaleResult):
    cfg = result.config
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    # Default to a pass-through so downstream stays valid while inputs are incomplete.
    result.data = data.copy()

    columns = cfg.column_selector[0]
    if columns in [None, []]:
        elements.column_selector.set_alert(0)
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
