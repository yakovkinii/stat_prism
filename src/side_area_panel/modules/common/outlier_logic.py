#  Copyright (c) 2023 StatPrism Team. All rights reserved.
"""Pure detection logic for the outlier steps.

Each detector takes a ``Data`` plus its parameters and returns an *ordered list of
candidate row IDs* proposed for removal. The same functions feed both the settings-panel
Remove-list (which turns the IDs into checkboxes) and the step's main() (which actually
drops them), so detection lives in one place and the two never drift apart.

Kept import-light and free of any Qt / UI dependency so the UI layer can import it
without a cycle.
"""

import numpy as np
import pandas as pd
from scipy import stats

from src.side_area_panel.modules.common.removal import ids_for_mask


def _univariate_mask(series: pd.Series, method: str, k: float) -> pd.Series:
    if method == "Z-score":
        std = series.std()
        if std == 0 or pd.isna(std):
            return pd.Series(False, index=series.index)
        return ((series - series.mean()).abs() / std) > k
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    return (series < q1 - k * iqr) | (series > q3 + k * iqr)


def detect_univariate_outliers(data, columns, method) -> list:
    """A row is a candidate if it is an outlier (IQR or Z-score) on any selected column."""
    columns = [c for c in (columns or []) if c in data.column_names()]
    if not columns:
        return []
    k = 1.5 if method != "Z-score" else 3.0

    outlier = None
    for column_name in columns:
        x = data.get_series(column_name, map_ordinal=True)
        column_outlier = _univariate_mask(x, method, k).fillna(False)
        outlier = column_outlier if outlier is None else (outlier | column_outlier)
    if outlier is None:
        return []
    return ids_for_mask(data, outlier)


def detect_grouped_outliers(data, columns, grouping_column, method) -> list:
    """Like univariate, but each value is judged against its own group's distribution."""
    columns = [c for c in (columns or []) if c in data.column_names()]
    if not columns or not grouping_column or grouping_column not in data.column_names():
        return []
    k = 1.5 if method != "Z-score" else 3.0
    group_labels = data[grouping_column].data_series

    def group_mask(series):
        return _univariate_mask(series, method, k)

    outlier = None
    for column_name in columns:
        x = data.get_series(column_name, map_ordinal=True)
        column_outlier = (
            x.groupby(group_labels, group_keys=False).transform(group_mask).fillna(False).astype(bool)
        )
        outlier = column_outlier if outlier is None else (outlier | column_outlier)
    if outlier is None:
        return []
    return ids_for_mask(data, outlier)


def detect_nd_outliers(data, columns, confidence=0.95) -> list:
    """Multivariate (N-dimensional) outliers via the Mahalanobis distance of each point
    from the joint centre, with a chi-square cutoff (df = number of columns). Needs at
    least two columns; returns [] otherwise."""
    columns = [c for c in (columns or []) if c in data.column_names()]
    if len(columns) < 2:
        return []

    frame = pd.concat(
        [data.get_series(column=c, map_ordinal=True) for c in columns], axis=1
    )
    outlier = pd.Series(False, index=frame.index)
    valid = ~frame.isna().any(axis=1)
    points = frame[valid].to_numpy()

    # Need more points than dimensions for a non-degenerate covariance estimate.
    if points.shape[0] >= len(columns) + 1:
        center = points.mean(axis=0)
        cov = np.cov(points, rowvar=False)
        try:
            inv_cov = np.linalg.inv(cov)
        except np.linalg.LinAlgError:
            inv_cov = np.linalg.pinv(cov)
        diff = points - center
        d2 = np.einsum("ij,jk,ik->i", diff, inv_cov, diff)
        threshold = stats.chi2.ppf(confidence, df=len(columns))
        outlier.loc[frame[valid].index] = d2 > threshold

    return ids_for_mask(data, outlier)
