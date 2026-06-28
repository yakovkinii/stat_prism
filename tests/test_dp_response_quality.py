#  Copyright (c) 2023 StatPrism Team. All rights reserved.
"""Snapshot tests for the Response Quality cleaning module."""

import pytest

from src.side_area_panel.modules.common.cleaning_logic import (
    CHECK_DUPLICATES,
    CHECK_LONGSTRING,
    CHECK_LOWVAR,
    CHECK_MISSING,
)
from src.side_area_panel.modules.dp_response_quality.dp_response_quality_main import dp_response_quality_main
from src.side_area_panel.modules.dp_response_quality.dp_response_quality_result import (
    ResponseQualityResult,
    ResponseQualityStudyConfig,
)
from tests.datasets import COL_AGE, COL_SATISFACTION, COL_SCORE, MAIN
from tests.helpers import assert_data_snapshot, load_dataset, run_main

_ITEMS = [COL_AGE, COL_SCORE, COL_SATISFACTION]


def _config(**overrides):
    base = dict(
        data_source="Auto",
        column_selector=[_ITEMS],
        check=CHECK_DUPLICATES,
        threshold=50,
        remove_list=None,
        enabled=True,
    )
    base.update(overrides)
    return ResponseQualityStudyConfig(**base)


CASES = [
    ("dp_quality_duplicates", dict(check=CHECK_DUPLICATES)),
    ("dp_quality_longstring", dict(check=CHECK_LONGSTRING, threshold=50)),
    ("dp_quality_missing", dict(check=CHECK_MISSING, threshold=50)),
    ("dp_quality_low_variability", dict(check=CHECK_LOWVAR, threshold=50)),
    ("dp_quality_disabled", dict(enabled=False)),
]


@pytest.mark.parametrize("name,overrides", CASES, ids=[c[0] for c in CASES])
def test_response_quality(name, overrides):
    result = run_main(dp_response_quality_main, ResponseQualityResult, _config(**overrides), load_dataset(MAIN))
    assert_data_snapshot(result, name)
