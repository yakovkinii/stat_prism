#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import pandas as pd

from src.common.decorators import log_function
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.dp_outliers.dp_outliers_result import OutliersResult
from src.side_area_panel.modules.dp_outliers.dp_outliers_ui import Elements


@log_function
def dp_outliers_main(elements: Elements, result: OutliersResult):
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
    if not selected:
        elements.column_selector.set_alert(0)
        return result

    method = cfg.method or "IQR"
    k = 1.5 if method == "IQR" else 3.0

    outlier = None
    for column_name in selected:
        x = pd.to_numeric(new_data[column_name].data_series, errors="coerce")
        if method == "Z-score":
            std = x.std()
            if std == 0 or pd.isna(std):
                column_outlier = pd.Series(False, index=x.index)
            else:
                column_outlier = ((x - x.mean()).abs() / std) > k
        else:  # IQR
            q1, q3 = x.quantile(0.25), x.quantile(0.75)
            iqr = q3 - q1
            column_outlier = (x < q1 - k * iqr) | (x > q3 + k * iqr)
        column_outlier = column_outlier.fillna(False)
        outlier = column_outlier if outlier is None else (outlier | column_outlier)

    if outlier is None:
        return result

    keep = ~outlier
    if "ID" in new_data.column_names():
        removed = new_data["ID"].data_series[outlier]
        result.removed_ids = [v.item() if hasattr(v, "item") else v for v in removed]
    for column in new_data.columns:
        column.data_series = column.data_series[keep]
    result.removed_count = int(outlier.sum())
    result.data = new_data
    return result
