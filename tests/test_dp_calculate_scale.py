#  Copyright (C) 2023-2026  StatPrism Team
#  Balashevych A. K., Petrova N. V., Yakovkin I. I.
#
#  This file is part of StatPrism.
#
#  StatPrism is free software: you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  StatPrism is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  StatPrism.  If not, see <https://www.gnu.org/licenses/>.
"""Snapshot tests for the Calculate Scale DP module."""

import pytest

from src.side_area_panel.modules.dp_calculate_scale.dp_calculate_scale_main import dp_calculate_scale_main
from src.side_area_panel.modules.dp_calculate_scale.dp_calculate_scale_result import (
    CalculateScaleResult,
    CalculateScaleStudyConfig,
)
from tests.datasets import COL_AGE, COL_SATISFACTION, COL_SCORE, MAIN
from tests.helpers import assert_data_snapshot, load_dataset, run_main

_ITEMS = [COL_AGE, COL_SCORE, COL_SATISFACTION]


# "Aggregate over present items regardless" is now expressed as the threshold mode at 100%
# (equivalent to the old exclude_missing=True). The default "Skip respondent" matches the old
# exclude_missing=False, so the existing snapshot outputs are unchanged.
_AGGREGATE = dict(missing_values="Allow up to max %", missing_threshold=100)


def _config(**overrides):
    base = dict(
        data_source="Auto",
        column_selector=[_ITEMS],
        name="Total scale",
        method="Sum",
        scale="None",
        questions_action="Keep",
        missing_values="Skip respondent",
        missing_threshold=0,
        color=None,
    )
    base.update(overrides)
    return CalculateScaleStudyConfig(**base)


CASES = [
    ("dp_scale_sum", dict(method="Sum")),
    ("dp_scale_mean", dict(method="Mean")),
    ("dp_scale_sum_exclude_missing", dict(method="Sum", **_AGGREGATE)),
    ("dp_scale_mean_exclude_missing", dict(method="Mean", **_AGGREGATE)),
    ("dp_scale_stanine", dict(method="Mean", scale="Stanine", **_AGGREGATE)),
]


@pytest.mark.parametrize("name,overrides", CASES, ids=[c[0] for c in CASES])
def test_calculate_scale(name, overrides):
    result = run_main(dp_calculate_scale_main, CalculateScaleResult, _config(**overrides), load_dataset(MAIN))
    assert_data_snapshot(result, name)
