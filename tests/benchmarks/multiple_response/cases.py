from __future__ import annotations

import pandas as pd

# 0/1 indicator columns for one multi-select question (same values mirrored in the R generator).
OPT_A = [1, 0, 1, 1, 0, 1, 0, 1, 1, 0]
OPT_B = [0, 1, 1, 0, 1, 1, 1, 0, 0, 1]
OPT_C = [1, 1, 0, 0, 0, 1, 0, 1, 0, 0]


def indicator_data() -> pd.DataFrame:
    return pd.DataFrame({"opt_a": OPT_A, "opt_b": OPT_B, "opt_c": OPT_C})


CASES = [
    {"study": "frequencies", "data": indicator_data, "columns": ["opt_a", "opt_b", "opt_c"],
     "kind": "multiple_response"},
]
