#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import math
import re

import pandas as pd

from src.common.constant import ColumnType
from src.common.decorators import log_function
from src.data.data import DataColumn
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.utility import unique_name
from src.side_area_panel.modules.dp_group.dp_group_result import GroupValuesResult
from src.side_area_panel.modules.dp_group.dp_group_ui import Elements


def _parse_floats(text):
    return [float(token) for token in re.split(r"[,;\s]+", (text or "").strip()) if token != ""]


def _auto_labels(thresholds):
    labels = [f"≤ {thresholds[0]:g}"]
    for low, high in zip(thresholds[:-1], thresholds[1:]):
        labels.append(f"{low:g}–{high:g}")
    labels.append(f"> {thresholds[-1]:g}")
    return labels


@log_function
def dp_group_main(elements: Elements, result: GroupValuesResult, update):
    cfg = result.config
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    new_data = data.copy()
    result.data = new_data

    selected = cfg.column_selector[0] if cfg.column_selector else None
    if not selected:
        elements.column_selector.set_alert(0)
        return result
    column_name = selected[0]

    try:
        thresholds = sorted(_parse_floats(cfg.thresholds))
    except ValueError:
        elements.thresholds.set_alert()
        return result
    if not thresholds:
        return result  # no split points -> no grouping

    expected = len(thresholds) + 1
    names = [n.strip() for n in re.split(r"[,;]", cfg.names) if n.strip()] if (cfg.names or "").strip() else []
    labels = names if len(names) == expected else _auto_labels(thresholds)

    edges = [-math.inf] + thresholds + [math.inf]
    numeric = pd.to_numeric(new_data[column_name].data_series, errors="coerce")
    binned = pd.cut(numeric, bins=edges, labels=labels, right=True, ordered=False).astype(object)

    base = (cfg.new_name or "").strip() or f"{column_name} (group)"
    binned.name = unique_name(base, set(new_data.column_names()))

    new_col = DataColumn.initialize_from_series(binned)
    new_col.column_type = ColumnType.ORDINAL
    new_col.order = {label: i + 1 for i, label in enumerate(labels)}
    new_col.automatically_update_order()
    # A grouped column is a derivative of its source, so it inherits the source's colour tag.
    new_col.color = new_data[column_name].color

    new_data.add_column_after(column_name, new_col)
    result.data = new_data
    return result
