#  Copyright (c) 2023 StatPrism Team. All rights reserved.
"""Snapshot tests for the Calculate Scale DP module."""

import pytest

from src.side_area_panel.modules.dp_calculate_scale.dp_calculate_scale_main import (
    dp_calculate_scale_main,
)
from src.side_area_panel.modules.dp_calculate_scale.dp_calculate_scale_result import (
    CalculateScaleResult,
    CalculateScaleStudyConfig,
)
from tests.datasets import COL_AGE, COL_SATISFACTION, COL_SCORE, MAIN
from tests.helpers import assert_data_snapshot, load_dataset, run_main

_ITEMS = [COL_AGE, COL_SCORE, COL_SATISFACTION]


def _config(**overrides):
    base = dict(
        data_source="Auto",
        column_selector=[_ITEMS],
        name="Total scale",
        method="Sum",
        scale="None",
        questions_action="Keep",
        exclude_missing=False,
        color=None,
        questions_color=None,
    )
    base.update(overrides)
    return CalculateScaleStudyConfig(**base)


CASES = [
    ("dp_scale_sum", dict(method="Sum")),
    ("dp_scale_mean", dict(method="Mean")),
    ("dp_scale_sum_exclude_missing", dict(method="Sum", exclude_missing=True)),
    ("dp_scale_mean_exclude_missing", dict(method="Mean", exclude_missing=True)),
    ("dp_scale_stanine", dict(method="Mean", scale="Stanine", exclude_missing=True)),
]


@pytest.mark.parametrize("name,overrides", CASES, ids=[c[0] for c in CASES])
def test_calculate_scale(name, overrides):
    result = run_main(dp_calculate_scale_main, CalculateScaleResult, _config(**overrides), load_dataset(MAIN))
    assert_data_snapshot(result, name)
