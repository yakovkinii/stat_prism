#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import pandas as pd

from src.common.decorators import log_function
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.dp_grouped_outliers.dp_grouped_outliers_result import (
    GroupedOutliersResult,
)
from src.side_area_panel.modules.dp_grouped_outliers.dp_grouped_outliers_ui import Elements


@log_function
def dp_grouped_outliers_main(elements: Elements, result: GroupedOutliersResult):
    """Exclude outliers computed *within each subgroup* of the grouping column. A row is
    dropped if it is an outlier (IQR or Z-score) on any selected column, judged against the
    distribution of its own group."""
    cfg = result.config
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    new_data = data.copy()
    result.data = new_data
    result.removed_count = 0
    result.removed_ids = []

    if not cfg.enabled:
        return result  # disabled -> no-op, stays in chain

    selected = cfg.column_selector[0] if cfg.column_selector else None
    grouping = cfg.column_selector[1] if (cfg.column_selector and len(cfg.column_selector) > 1) else None
    if not selected:
        elements.column_selector.set_alert(0)
        return result
    if not grouping:
        elements.column_selector.set_alert(1)
        return result
    grouping_column = grouping[0]

    method = cfg.method or "IQR"
    k = 1.5 if method == "IQR" else 3.0
    group_labels = new_data[grouping_column].data_series

    def group_mask(series):
        # Outlier mask for one group's values (NaNs never flagged).
        if method == "Z-score":
            std = series.std()
            if std == 0 or pd.isna(std):
                return pd.Series(False, index=series.index)
            return ((series - series.mean()).abs() / std) > k
        q1, q3 = series.quantile(0.25), series.quantile(0.75)
        iqr = q3 - q1
        return (series < q1 - k * iqr) | (series > q3 + k * iqr)

    outlier = None
    for column_name in selected:
        x = new_data.get_series(column_name, map_ordinal=True)
        # transform keeps the result aligned to x's index, one mask per group
        column_outlier = x.groupby(group_labels, group_keys=False).transform(group_mask).fillna(False).astype(bool)
        outlier = column_outlier if outlier is None else (outlier | column_outlier)

    if outlier is None:
        return result

    keep = ~outlier
    removed = new_data.get_id_series()[outlier]
    result.removed_ids = [v.item() if hasattr(v, "item") else v for v in removed]
    for column in new_data.columns:
        column.data_series = column.data_series[keep]
    result.removed_count = int(outlier.sum())
    result.data = new_data
    return result
