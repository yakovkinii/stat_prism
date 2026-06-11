#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import numpy as np
import pandas as pd
from scipy import stats

from src.common.decorators import log_function
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.dp_2d_outliers.dp_2d_outliers_result import TwoDOutliersResult
from src.side_area_panel.modules.dp_2d_outliers.dp_2d_outliers_ui import Elements

# Mahalanobis cutoff: chi-square (df = 2) at 95% confidence.
_CONFIDENCE = 0.95


@log_function
def dp_2d_outliers_main(elements: Elements, result: TwoDOutliersResult):
    """Exclude multivariate (2D) outliers using the Mahalanobis distance: a row is dropped
    when the squared Mahalanobis distance of its (x, y) pair from the joint centre exceeds
    the chi-square cutoff (df = 2) at the chosen confidence. This accounts for the
    correlation between the two columns, unlike per-column thresholds."""
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

    cols1 = cfg.column_selector[0] if cfg.column_selector else None
    cols2 = cfg.column_selector[1] if (cfg.column_selector and len(cfg.column_selector) > 1) else None
    if not cols1:
        elements.column_selector.set_alert(0)
        return result
    if not cols2:
        elements.column_selector.set_alert(1)
        return result
    col_x, col_y = cols1[0], cols2[0]
    if col_x == col_y:
        elements.column_selector.set_alert(1)
        return result

    threshold = stats.chi2.ppf(_CONFIDENCE, df=2)

    x = pd.to_numeric(new_data[col_x].data_series, errors="coerce")
    y = pd.to_numeric(new_data[col_y].data_series, errors="coerce")

    outlier = pd.Series(False, index=x.index)
    valid = ~(x.isna() | y.isna())
    points = np.column_stack([x[valid].to_numpy(), y[valid].to_numpy()])

    # Need at least a few points and non-degenerate spread to estimate the covariance.
    if points.shape[0] >= 3:
        center = points.mean(axis=0)
        cov = np.cov(points, rowvar=False)
        try:
            inv_cov = np.linalg.inv(cov)
        except np.linalg.LinAlgError:
            inv_cov = np.linalg.pinv(cov)
        diff = points - center
        d2 = np.einsum("ij,jk,ik->i", diff, inv_cov, diff)
        outlier.loc[x[valid].index] = d2 > threshold

    keep = ~outlier
    if "ID" in new_data.column_names():
        removed = new_data["ID"].data_series[outlier]
        result.removed_ids = [v.item() if hasattr(v, "item") else v for v in removed]
    for column in new_data.columns:
        column.data_series = column.data_series[keep]
    result.removed_count = int(outlier.sum())
    result.data = new_data
    return result
