#  Copyright (c) 2023 StatPrism Team. All rights reserved.
"""Snapshot tests for the Impute Missing DP module."""

import pytest

from src.side_area_panel.modules.dp_impute.dp_impute_main import dp_impute_main
from src.side_area_panel.modules.dp_impute.dp_impute_result import ImputeResult, ImputeStudyConfig
from tests.datasets import COL_AGE, COL_INCOME, MAIN
from tests.helpers import assert_data_snapshot, load_dataset, run_main


def _config(**overrides):
    base = dict(
        data_source="Auto",
        column_selector=[[COL_AGE, COL_INCOME]],
        method="Mean",
        constant_value="",
    )
    base.update(overrides)
    return ImputeStudyConfig(**base)


CASES = [
    ("dp_impute_mean", dict(method="Mean")),
    ("dp_impute_median", dict(method="Median")),
    ("dp_impute_mode", dict(method="Mode")),
    ("dp_impute_constant", dict(method="Constant value", constant_value="0")),
]


@pytest.mark.parametrize("name,overrides", CASES, ids=[c[0] for c in CASES])
def test_impute(name, overrides):
    result = run_main(dp_impute_main, ImputeResult, _config(**overrides), load_dataset(MAIN))
    assert_data_snapshot(result, name)
