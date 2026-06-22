#  Copyright (c) 2023 StatPrism Team. All rights reserved.
"""Snapshot tests for the Invert Scale DP module."""

import pytest

from src.side_area_panel.modules.dp_invert_scale.dp_invert_scale_main import (
    dp_invert_scale_main,
)
from src.side_area_panel.modules.dp_invert_scale.dp_invert_scale_result import (
    InvertScaleResult,
    InvertScaleStudyConfig,
)
from tests.datasets import COL_SATISFACTION, COL_SCORE, MAIN
from tests.helpers import assert_data_snapshot, load_dataset, run_main


def _config(**overrides):
    base = dict(
        data_source="Auto",
        column_selector=[[COL_SATISFACTION]],
        reference=None,  # auto = max + min
    )
    base.update(overrides)
    return InvertScaleStudyConfig(**base)


CASES = [
    ("dp_invert_satisfaction_auto", dict()),
    ("dp_invert_satisfaction_ref6", dict(reference=6)),
    ("dp_invert_multiple", dict(column_selector=[[COL_SATISFACTION, COL_SCORE]])),
]


@pytest.mark.parametrize("name,overrides", CASES, ids=[c[0] for c in CASES])
def test_invert_scale(name, overrides):
    result = run_main(dp_invert_scale_main, InvertScaleResult, _config(**overrides), load_dataset(MAIN))
    assert_data_snapshot(result, name)
