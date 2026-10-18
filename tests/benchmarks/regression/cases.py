from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).resolve().parent / "data" / "regression_data.csv"


def regression_data() -> pd.DataFrame:
    # Static fixture read identically by Python (here) and R (the generator), so the two sides fit the
    # same numbers. Columns: x1, x2, med (numeric), y (numeric outcome), bin (yes/no), cat (A/B/C).
    return pd.read_csv(DATA_PATH)


# dep/indeps/mod/med fill the four column-selector groups. model is the RegressionModelType value.
# A single linear run emits the fit / coefficients / VIF / influence supplements; each case reads one.
CASES = [
    {"study": "linear_fit", "model": "linear", "dep": "y", "indeps": ["x1", "x2"],
     "kind": "regression_linear_fit"},
    {"study": "linear_coef", "model": "linear", "dep": "y", "indeps": ["x1", "x2"],
     "kind": "regression_linear_coef"},
    {"study": "linear_vif", "model": "linear", "dep": "y", "indeps": ["x1", "x2"],
     "kind": "regression_vif"},
    {"study": "linear_influence", "model": "linear", "dep": "y", "indeps": ["x1", "x2"],
     "kind": "regression_influence"},
    {"study": "moderation_coef", "model": "linear", "dep": "y", "indeps": ["x1"], "mod": "x2",
     "kind": "regression_linear_coef"},
    {"study": "mediation_paths", "model": "linear", "dep": "y", "indeps": ["x1"], "med": "med",
     "kind": "regression_paths"},
    {"study": "logistic_fit", "model": "logistic", "dep": "bin", "indeps": ["x1", "x2"],
     "kind": "regression_logistic_fit"},
    {"study": "logistic_coef", "model": "logistic", "dep": "bin", "indeps": ["x1", "x2"],
     "kind": "regression_logistic_coef"},
    {"study": "multinomial_fit", "model": "multinomial", "dep": "cat", "indeps": ["x1", "x2"],
     "kind": "regression_multinomial_fit"},
    {"study": "multinomial_coef", "model": "multinomial", "dep": "cat", "indeps": ["x1", "x2"],
     "kind": "regression_multinomial_coef"},
]
