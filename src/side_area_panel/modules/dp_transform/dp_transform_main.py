#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import numpy as np
import pandas as pd

from src.common.decorators import log_function
from src.data.data import DataColumn
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.utility import unique_name
from src.side_area_panel.modules.dp_transform.dp_transform_result import TransformResult
from src.side_area_panel.modules.dp_transform.dp_transform_ui import Elements


def _apply_transform(series: pd.Series, transform: str) -> pd.Series:
    x = pd.to_numeric(series, errors="coerce")
    if transform == "Z-score":
        std = x.std()
        return (x - x.mean()) / std if std else x - x.mean()
    if transform == "Center":
        return x - x.mean()
    if transform == "Min-max":
        span = x.max() - x.min()
        return (x - x.min()) / span if span else x - x.min()
    if transform == "Log":
        return np.log(x.where(x > 0))
    if transform == "Rank":
        return x.rank(method="average")
    if transform == "Flip":
        return (x.max() + x.min()) - x
    raise ValueError(f"Unknown transform: {transform}")


@log_function
def dp_transform_main(elements: Elements, result: TransformResult, update):
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

    transform = cfg.transform or "Z-score"
    transformed = _apply_transform(new_data[column_name].data_series, transform)

    base_name = (cfg.new_name or "").strip() or f"{column_name} ({transform.lower()})"
    new_name = unique_name(base_name, set(new_data.column_names()))
    transformed = transformed.copy()
    transformed.name = new_name

    new_column = DataColumn.initialize_from_series(transformed)
    new_data.add_column_after(column_name, new_column)

    result.data = new_data
    return result
