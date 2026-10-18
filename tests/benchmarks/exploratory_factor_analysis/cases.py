from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).resolve().parent / "data" / "efa_data.csv"


def efa_data() -> pd.DataFrame:
    # 6 items with a clean 2-factor structure (v1-v3 / v4-v6), read identically by Python and R.
    return pd.read_csv(DATA_PATH)


# All three studies come from one EFA run: Pearson correlation, MINRES extraction, NO rotation
# (rotation conventions between factor_analyzer and psych differ and are deferred to a later pass),
# 2 factors. Diagnostics and eigenvalues share the same formulas as psych; loadings are compared after
# a canonical sign/column alignment because the raw sign and factor order are not identified.
CASES = [
    {"study": "diagnostics", "kind": "efa_diagnostics"},
    {"study": "eigenvalues", "kind": "efa_eigenvalues"},
    {"study": "loadings_unrotated", "kind": "efa_loadings"},
]
