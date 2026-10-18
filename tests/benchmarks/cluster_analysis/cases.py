from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).resolve().parent / "data" / "cluster_data.csv"


def cluster_data() -> pd.DataFrame:
    # Three well-separated 2-D blobs (read identically by Python and R) so Ward linkage and the
    # 3-cluster cut are unambiguous -- no tie-breaking ambiguity between scipy and R.
    return pd.read_csv(DATA_PATH)


# Only the deterministic hierarchical path is benchmarked (KMeans is reproducible via random_state=0
# but not cross-validated against R). standardize off so no sd-convention (ddof) mismatch arises.
CASES = [
    {"study": "hierarchical_ward", "method": "Hierarchical", "linkage": "Ward", "k": 3,
     "kind": "cluster_hierarchical"},
]
