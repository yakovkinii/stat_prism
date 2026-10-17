from __future__ import annotations

from types import SimpleNamespace

import pandas as pd

# Four-item scales throughout: with omega on, "omega if item dropped" is computed on the remaining
# three items, where the single-common-factor model is identified. (A three-item scale would leave a
# two-item submatrix, where that model is under-identified and StatPrism and psych legitimately differ.)
LIKERT_ITEMS = ["item_a", "item_b", "item_c", "item_d"]
BINARY_ITEMS = ["bin_a", "bin_b", "bin_c", "bin_d"]
ORDINAL_ITEMS = ["ord_a", "ord_b", "ord_c", "ord_d"]


def likert_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "item_a": [1, 2, 2, 3, 4, 4, 5, 5, 4, 3],
            "item_b": [1, 2, 3, 3, 4, 5, 5, 5, 4, 4],
            "item_c": [2, 2, 3, 3, 4, 4, 5, 5, 5, 4],
            "item_d": [1, 1, 2, 3, 3, 4, 4, 5, 4, 3],
        }
    )


def binary_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "bin_a": [0, 0, 1, 1, 1, 0, 1, 0, 1, 1],
            "bin_b": [0, 1, 1, 1, 1, 0, 1, 0, 1, 0],
            "bin_c": [0, 0, 1, 0, 1, 0, 1, 0, 1, 1],
            "bin_d": [0, 0, 1, 1, 1, 0, 1, 1, 1, 0],
        }
    )


def ordinal_string_data() -> pd.DataFrame:
    df = likert_data()
    df.columns = ORDINAL_ITEMS
    return df.astype(str)


def config(items, correlation_type="Pearson", omega=True) -> SimpleNamespace:
    return SimpleNamespace(
        data_source="Auto",
        column_selector=[list(items)],
        correlation_type=correlation_type,
        scale_name="Benchmark scale",
        mcdonald_omega=omega,
        item_deleted_table=True,
        verbal_indicators=False,
        interpretation=None,
        number_columns=False,
    )


CASES = [
    {
        "study": "pearson_four_items_with_omega",
        "data": likert_data,
        "config": lambda: config(LIKERT_ITEMS, correlation_type="Pearson", omega=True),
    },
    {
        "study": "pearson_ordinal_string_items_with_omega",
        "data": ordinal_string_data,
        "ordinal_order": {column: ["1", "2", "3", "4", "5"] for column in ORDINAL_ITEMS},
        "config": lambda: config(ORDINAL_ITEMS, correlation_type="Pearson", omega=True),
    },
    {
        "study": "spearman_four_items_with_omega",
        "data": likert_data,
        "config": lambda: config(LIKERT_ITEMS, correlation_type="Spearman", omega=True),
    },
    {
        "study": "kendall_four_items_with_omega",
        "data": likert_data,
        "config": lambda: config(LIKERT_ITEMS, correlation_type="Kendall", omega=True),
    },
    {
        "study": "kendall_tau_c_four_items_with_omega",
        "data": likert_data,
        "config": lambda: config(LIKERT_ITEMS, correlation_type="Kendall tau c", omega=True),
    },
    {
        "study": "phi_binary_items_with_omega",
        "data": binary_data,
        "config": lambda: config(BINARY_ITEMS, correlation_type="Phi", omega=True),
    },
    {
        "study": "tetrachoric_binary_items_with_omega",
        "data": binary_data,
        "config": lambda: config(BINARY_ITEMS, correlation_type="Tetrachoric", omega=True),
    },
    {
        "study": "polychoric_likert_items_with_omega",
        "data": likert_data,
        "config": lambda: config(LIKERT_ITEMS, correlation_type="Polychoric", omega=True),
    },
]
