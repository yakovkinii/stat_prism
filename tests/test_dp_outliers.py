#  Copyright (c) 2023 StatPrism Team. All rights reserved.
"""Snapshot tests for the Outliers DP module."""

import pytest

from src.side_area_panel.modules.dp_outliers.dp_outliers_main import dp_outliers_main
from src.side_area_panel.modules.dp_outliers.dp_outliers_result import (
    OutliersResult,
    OutliersStudyConfig,
)
from tests.datasets import COL_INCOME, COL_SCORE, MAIN
from tests.helpers import assert_data_snapshot, load_dataset, run_main


def _config(**overrides):
    base = dict(
        data_source="Auto",
        column_selector=[[COL_INCOME]],
        method="IQR",
        enabled=True,
    )
    base.update(overrides)
    return OutliersStudyConfig(**base)


CASES = [
    ("dp_outliers_iqr", dict(method="IQR")),
    ("dp_outliers_zscore", dict(method="Z-score")),
    ("dp_outliers_multi", dict(column_selector=[[COL_INCOME, COL_SCORE]], method="IQR")),
    ("dp_outliers_disabled", dict(enabled=False)),
]


@pytest.mark.parametrize("name,overrides", CASES, ids=[c[0] for c in CASES])
def test_outliers(name, overrides):
    result = run_main(dp_outliers_main, OutliersResult, _config(**overrides), load_dataset(MAIN))
    assert_data_snapshot(result, name)
