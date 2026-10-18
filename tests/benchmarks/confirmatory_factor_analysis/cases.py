from __future__ import annotations

from pathlib import Path

import pandas as pd

_DIR = Path(__file__).resolve().parent / "data"
ML_DATA_PATH = _DIR / "cfa_data.csv"
DWLS_DATA_PATH = _DIR / "cfa_dwls_data.csv"


def cfa_data() -> pd.DataFrame:
    # Continuous 6-item, 2-factor data (ML case), read identically by Python and R.
    return pd.read_csv(ML_DATA_PATH)


def cfa_dwls_data() -> pd.DataFrame:
    # Five-category Likert data (DWLS case).
    return pd.read_csv(DWLS_DATA_PATH)


ML = "Maximum Likelihood (ML)"
DWLS = "Diagonally Weighted LS (DWLS)"

# ML: two correlated factors. Standardized loadings / factor correlation are robust to the
# identification choice; fit indices carry convention risk (chi-square scaling, SRMR flavor).
# DWLS: StatPrism fits semopy's DWLS on the standardized order codes (NOT polychoric correlations),
# then mean-and-variance (WLSMV) scales the fit indices. The closest trusted reference is lavaan's
# WLSMV on the same values; because semopy is not polychoric-based these are compared loosely.
CASES = [
    {"study": "cfa_fit", "estimator": ML, "data": cfa_data, "kind": "cfa_fit"},
    {"study": "cfa_loadings", "estimator": ML, "data": cfa_data, "kind": "cfa_loadings"},
    {"study": "cfa_phi", "estimator": ML, "data": cfa_data, "kind": "cfa_phi"},
    {"study": "cfa_dwls_fit", "estimator": DWLS, "data": cfa_dwls_data, "kind": "cfa_fit"},
    {"study": "cfa_dwls_loadings", "estimator": DWLS, "data": cfa_dwls_data, "kind": "cfa_loadings"},
    {"study": "cfa_dwls_phi", "estimator": DWLS, "data": cfa_dwls_data, "kind": "cfa_phi"},
]
