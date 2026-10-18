from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).resolve().parent / "data" / "sem_data.csv"


def sem_data() -> pd.DataFrame:
    # 6 items, two latent factors (F1 = v1-v3, F2 = v4-v6) where F2 depends on F1 (standardized path
    # ~0.5), so the structural coefficient is well away from zero. Read identically by Python and R.
    return pd.read_csv(DATA_PATH)


# One ML SEM: measurement model for F1, F2 plus a structural regression F2 ~ F1. Standardized loadings
# and the structural path match lavaan closely; fit indices carry the same convention caveats as CFA.
CASES = [
    {"study": "sem_fit", "kind": "sem_fit"},
    {"study": "sem_params", "kind": "sem_params"},
]
