from __future__ import annotations

import pandas as pd

# Each contingency "dataset" is a cross-tab of counts; the module expects raw observations, so the
# matrices below are expanded back to one row per observation. Category values (not the column names)
# define the axis labels, so the square tables reuse the same label set on both columns for McNemar.

# A 2x3 table with a clear association (drives a significant chi-square, so the residuals appear).
TABLE_2x3 = {"r1": {"c1": 20, "c2": 5, "c3": 10}, "r2": {"c1": 5, "c2": 20, "c3": 10}}
# A small 2x2 table with an expected count below 5, so Fisher's exact test is reported.
TABLE_2x2 = {"r1": {"c1": 8, "c2": 2}, "r2": {"c1": 1, "c2": 9}}
# A 2x2 square (shared labels) with 30 discordant pairs -- >= 25, so statsmodels uses the chi-square
# McNemar (not the exact binomial), matching R's mcnemar.test.
SQUARE_2x2 = {"a": {"a": 30, "b": 20}, "b": {"a": 10, "b": 40}}
# A 2x2 square with only 9 discordant pairs -- < 25, so statsmodels switches to the EXACT binomial
# McNemar (statistic = min(b, c), p = two-sided binomial), which the generator matches with binom.test.
SQUARE_2x2_SMALL = {"a": {"a": 20, "b": 3}, "b": {"a": 6, "b": 25}}
# A 3x3 square (shared labels) with asymmetric off-diagonals -> Bowker's symmetry test.
SQUARE_3x3 = {
    "a": {"a": 10, "b": 6, "c": 2},
    "b": {"a": 3, "b": 12, "c": 5},
    "c": {"a": 1, "b": 4, "c": 15},
}


def _expand(matrix: dict) -> pd.DataFrame:
    rows = list(matrix.keys())
    cols = list(next(iter(matrix.values())).keys())
    records = []
    for r in rows:
        for c in cols:
            records.extend([(r, c)] * matrix[r][c])
    return pd.DataFrame(records, columns=["v1", "v2"])


def table_2x3() -> pd.DataFrame:
    return _expand(TABLE_2x3)


def table_2x2() -> pd.DataFrame:
    return _expand(TABLE_2x2)


def square_2x2() -> pd.DataFrame:
    return _expand(SQUARE_2x2)


def square_2x2_small() -> pd.DataFrame:
    return _expand(SQUARE_2x2_SMALL)


def square_3x3() -> pd.DataFrame:
    return _expand(SQUARE_3x3)


# method tokens map to config flags in run.py. Each case names the supplement `kind` to read.
CASES = [
    {"study": "counts", "data": table_2x3, "kind": "contingency_counts"},
    {"study": "percent_row", "data": table_2x3, "percentages": "Row %", "kind": "contingency_percent"},
    {"study": "percent_col", "data": table_2x3, "percentages": "Column %", "kind": "contingency_percent"},
    {"study": "percent_total", "data": table_2x3, "percentages": "Total %", "kind": "contingency_percent"},
    {"study": "chi2_2x3", "data": table_2x3, "kind": "contingency_chi2"},
    {"study": "residuals", "data": table_2x3, "post_hoc": True, "kind": "contingency_residuals"},
    # 2x2 with continuity correction + Fisher's exact (interpretation on so Fisher is computed).
    {
        "study": "chi2_2x2_fisher",
        "data": table_2x2,
        "correction": True,
        "interpretation": "Full",
        "kind": "contingency_chi2",
    },
    {"study": "mcnemar_2x2", "data": square_2x2, "mcnemar": True, "correction": True, "kind": "contingency_mcnemar"},
    {"study": "mcnemar_exact", "data": square_2x2_small, "mcnemar": True, "kind": "contingency_mcnemar"},
    {"study": "bowker_3x3", "data": square_3x3, "mcnemar": True, "kind": "contingency_mcnemar"},
]
