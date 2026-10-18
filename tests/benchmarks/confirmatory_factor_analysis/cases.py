from __future__ import annotations

from pathlib import Path

import pandas as pd

_DIR = Path(__file__).resolve().parent / "data"
ML_DATA_PATH = _DIR / "cfa_data.csv"
DWLS_DATA_PATH = _DIR / "cfa_dwls_data.csv"
THREE_FACTOR_DATA_PATH = _DIR / "cfa_3factor_data.csv"


def cfa_data() -> pd.DataFrame:
    # Continuous 6-item, 2-factor data (ML case), read identically by Python and R.
    return pd.read_csv(ML_DATA_PATH)


def cfa_dwls_data() -> pd.DataFrame:
    # Five-category Likert data (DWLS case).
    return pd.read_csv(DWLS_DATA_PATH)


def cfa_3factor_data() -> pd.DataFrame:
    # 9 items, 3 first-order factors driven by a general factor (second-order case).
    return pd.read_csv(THREE_FACTOR_DATA_PATH)


ML = "Maximum Likelihood (ML)"
DWLS = "Diagonally Weighted LS (DWLS)"
ULS = "Unweighted LS (polychoric)"

# ML: two correlated factors on continuous data. Standardized loadings / factor correlation are robust
# to the identification choice; fit indices carry convention risk (chi-square scaling, SRMR flavor).
# DWLS: robust-continuous -- semopy DWLS on the standardized item values + WLSMV-scaled fit indices;
# the closest trusted reference is lavaan WLSMV on the same values as continuous (compared loosely).
# ULS: the ordinal estimator -- ULS on the in-house polychoric matrix. Benchmark the honest outputs
# (standardized loadings + factor correlation) against lavaan estimator="ULS" with ordered items;
# the fit indices are naive (non-robust) on both sides, so they are not benchmarked for ULS.
CASES = [
    {"study": "cfa_fit", "estimator": ML, "data": cfa_data, "kind": "cfa_fit"},
    {"study": "cfa_loadings", "estimator": ML, "data": cfa_data, "kind": "cfa_loadings"},
    {"study": "cfa_phi", "estimator": ML, "data": cfa_data, "kind": "cfa_phi"},
    {"study": "cfa_dwls_fit", "estimator": DWLS, "data": cfa_dwls_data, "kind": "cfa_fit"},
    {"study": "cfa_dwls_loadings", "estimator": DWLS, "data": cfa_dwls_data, "kind": "cfa_loadings"},
    {"study": "cfa_dwls_phi", "estimator": DWLS, "data": cfa_dwls_data, "kind": "cfa_phi"},
    {"study": "cfa_uls_loadings", "estimator": ULS, "data": cfa_dwls_data, "kind": "cfa_loadings"},
    {"study": "cfa_uls_phi", "estimator": ULS, "data": cfa_dwls_data, "kind": "cfa_phi"},
    # Orthogonal model: factor covariance fixed to 0 -> distinct loadings branch.
    {
        "study": "cfa_orthogonal_loadings",
        "estimator": ML,
        "data": cfa_data,
        "allow_factor_correlation": False,
        "kind": "cfa_loadings",
    },
    # Second-order factor (3 first-order factors + a general factor G).
    {
        "study": "cfa_second_order",
        "estimator": ML,
        "data": cfa_3factor_data,
        "structure": [["v1", "v2", "v3"], ["v4", "v5", "v6"], ["v7", "v8", "v9"]],
        "second_order": True,
        "kind": "cfa_second_order",
    },
    # Applied cross-loading: v3 also loads on F2 (factor index 1).
    {
        "study": "cfa_cross_loading_loadings",
        "estimator": ML,
        "data": cfa_data,
        "cross_loadings": [["v3", 1]],
        "kind": "cfa_loadings",
    },
    # Freed residual correlation between v1 and v2.
    {
        "study": "cfa_residual_fit",
        "estimator": ML,
        "data": cfa_data,
        "residual_correlations": [["v1", "v2"]],
        "kind": "cfa_fit",
    },
]
