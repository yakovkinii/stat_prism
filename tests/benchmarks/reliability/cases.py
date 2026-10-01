from __future__ import annotations

from types import SimpleNamespace

import pandas as pd

LIKERT_ITEMS = ["item_a", "item_b", "item_c", "item_d"]
BINARY_ITEMS = ["bin_a", "bin_b", "bin_c"]
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
        "study": "spearman_three_items_no_omega",
        "data": likert_data,
        "config": lambda: config(LIKERT_ITEMS[:3], correlation_type="Spearman", omega=False),
    },
    {
        "study": "kendall_three_items_no_omega",
        "data": likert_data,
        "config": lambda: config(LIKERT_ITEMS[:3], correlation_type="Kendall", omega=False),
    },
    {
        "study": "kendall_tau_c_three_items_no_omega",
        "data": likert_data,
        "config": lambda: config(LIKERT_ITEMS[:3], correlation_type="Kendall tau c", omega=False),
    },
    {
        "study": "phi_binary_items_no_omega",
        "data": binary_data,
        "config": lambda: config(BINARY_ITEMS, correlation_type="Phi", omega=False),
    },
    {
        "study": "tetrachoric_binary_items_no_omega",
        "data": binary_data,
        "config": lambda: config(BINARY_ITEMS, correlation_type="Tetrachoric", omega=False),
    },
    {
        "study": "polychoric_likert_items_no_omega",
        "data": likert_data,
        "config": lambda: config(LIKERT_ITEMS[:3], correlation_type="Polychoric", omega=False),
    },
]
