from __future__ import annotations

import pandas as pd

LIKERT = ["col_a", "col_b", "col_c", "col_d"]
BINARY = ["bin_a", "bin_b", "bin_c"]


def likert_data() -> pd.DataFrame:
    # Same figures as the reliability benchmark so the R psych estimates stay well-conditioned.
    return pd.DataFrame(
        {
            "col_a": [1, 2, 2, 3, 4, 4, 5, 5, 4, 3],
            "col_b": [1, 2, 3, 3, 4, 5, 5, 5, 4, 4],
            "col_c": [2, 2, 3, 3, 4, 4, 5, 5, 5, 4],
            "col_d": [1, 1, 2, 3, 3, 4, 4, 5, 4, 3],
        }
    )


def binary_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "bin_a": [0, 0, 1, 1, 1, 0, 1, 0, 1, 1],
            "bin_b": [0, 1, 1, 1, 1, 0, 1, 0, 1, 0],
            "bin_c": [0, 0, 1, 0, 1, 0, 1, 0, 1, 1],
        }
    )


# Each case names its data, coefficient, layout (square / partial / cross / partial_cross) and the
# columns involved. run.py drives the matching calculate_* function and compares the per-pair r
# values against the R benchmark keyed by "<row>__<col>".
CASES = [
    {
        "study": "pearson_square",
        "data": likert_data,
        "correlation_type": "Pearson",
        "mode": "square",
        "columns": LIKERT,
    },
    {
        "study": "spearman_square",
        "data": likert_data,
        "correlation_type": "Spearman",
        "mode": "square",
        "columns": LIKERT,
    },
    {
        "study": "kendall_square",
        "data": likert_data,
        "correlation_type": "Kendall",
        "mode": "square",
        "columns": LIKERT,
    },
    {
        "study": "kendall_tau_c_square",
        "data": likert_data,
        "correlation_type": "Kendall tau c",
        "mode": "square",
        "columns": LIKERT,
    },
    {
        "study": "phi_square",
        "data": binary_data,
        "correlation_type": "Phi",
        "mode": "square",
        "columns": BINARY,
    },
    {
        "study": "tetrachoric_square",
        "data": binary_data,
        "correlation_type": "Tetrachoric",
        "mode": "square",
        "columns": BINARY,
    },
    {
        "study": "polychoric_square",
        "data": likert_data,
        "correlation_type": "Polychoric",
        "mode": "square",
        "columns": ["col_a", "col_b", "col_c"],
    },
    {
        "study": "pearson_partial",
        "data": likert_data,
        "correlation_type": "Pearson",
        "mode": "partial",
        "columns": ["col_a", "col_b", "col_c"],
        "controls": ["col_d"],
    },
    {
        "study": "spearman_partial",
        "data": likert_data,
        "correlation_type": "Spearman",
        "mode": "partial",
        "columns": ["col_a", "col_b", "col_c"],
        "controls": ["col_d"],
    },
    {
        "study": "pearson_cross",
        "data": likert_data,
        "correlation_type": "Pearson",
        "mode": "cross",
        "rows": ["col_a", "col_b"],
        "cols": ["col_c", "col_d"],
    },
    {
        "study": "spearman_partial_cross",
        "data": likert_data,
        "correlation_type": "Spearman",
        "mode": "partial_cross",
        "rows": ["col_a", "col_b"],
        "cols": ["col_c"],
        "controls": ["col_d"],
    },
    {
        "study": "pearson_partial_cross",
        "data": likert_data,
        "correlation_type": "Pearson",
        "mode": "partial_cross",
        "rows": ["col_a", "col_b"],
        "cols": ["col_c"],
        "controls": ["col_d"],
    },
    {
        "study": "spearman_cross",
        "data": likert_data,
        "correlation_type": "Spearman",
        "mode": "cross",
        "rows": ["col_a", "col_b"],
        "cols": ["col_c", "col_d"],
    },
    {
        "study": "kendall_cross",
        "data": likert_data,
        "correlation_type": "Kendall",
        "mode": "cross",
        "rows": ["col_a", "col_b"],
        "cols": ["col_c", "col_d"],
    },
    {
        "study": "kendall_tau_c_cross",
        "data": likert_data,
        "correlation_type": "Kendall tau c",
        "mode": "cross",
        "rows": ["col_a", "col_b"],
        "cols": ["col_c", "col_d"],
    },
    {
        "study": "phi_cross",
        "data": binary_data,
        "correlation_type": "Phi",
        "mode": "cross",
        "rows": ["bin_a", "bin_b"],
        "cols": ["bin_c"],
    },
    {
        "study": "tetrachoric_cross",
        "data": binary_data,
        "correlation_type": "Tetrachoric",
        "mode": "cross",
        "rows": ["bin_a", "bin_b"],
        "cols": ["bin_c"],
    },
    {
        "study": "polychoric_cross",
        "data": likert_data,
        "correlation_type": "Polychoric",
        "mode": "cross",
        "rows": ["col_a", "col_b"],
        "cols": ["col_c"],
    },
]
