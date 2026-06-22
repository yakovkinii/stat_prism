#  Copyright (c) 2023 StatPrism Team. All rights reserved.
"""Snapshot tests for the Filter DP module."""

import pytest

from src.side_area_panel.modules.dp_filter.dp_filter_main import dp_filter_main
from src.side_area_panel.modules.dp_filter.dp_filter_result import (
    FilterDataResult,
    FilterDataStudyConfig,
)
from tests.datasets import COL_AGE, COL_REGION, COL_SATISFACTION, MAIN
from tests.helpers import assert_data_snapshot, load_dataset, run_main


def _config(column, column_filter, enabled=True):
    return FilterDataStudyConfig(
        data_source="Auto",
        column_selector=[[column]],
        column_filter=column_filter,
        enabled=enabled,
    )


CASES = [
    ("dp_filter_numeric_gt", _config(COL_AGE, {"column": COL_AGE, "mode": "numeric", "operation": ">", "value": "30"})),
    ("dp_filter_numeric_le", _config(COL_AGE, {"column": COL_AGE, "mode": "numeric", "operation": "<=", "value": "40"})),
    ("dp_filter_numeric_in", _config(COL_SATISFACTION, {"column": COL_SATISFACTION, "mode": "numeric", "operation": "==", "value": "4, 5"})),
    ("dp_filter_numeric_not_in", _config(COL_SATISFACTION, {"column": COL_SATISFACTION, "mode": "numeric", "operation": "!=", "value": "1"})),
    ("dp_filter_is_empty", _config(COL_AGE, {"column": COL_AGE, "mode": "numeric", "operation": "is empty"})),
    ("dp_filter_not_empty", _config(COL_AGE, {"column": COL_AGE, "mode": "numeric", "operation": "is not empty"})),
    ("dp_filter_categorical", _config(COL_REGION, {"column": COL_REGION, "mode": "categorical", "kept_values": ["North", "South"]})),
    ("dp_filter_disabled", _config(COL_AGE, {"column": COL_AGE, "mode": "numeric", "operation": ">", "value": "30"}, enabled=False)),
]


@pytest.mark.parametrize("name,config", CASES, ids=[c[0] for c in CASES])
def test_filter(name, config):
    result = run_main(dp_filter_main, FilterDataResult, config, load_dataset(MAIN))
    assert_data_snapshot(result, name)
