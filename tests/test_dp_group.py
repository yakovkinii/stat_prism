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
"""Snapshot tests for the Group Values DP module."""

import pytest

from src.side_area_panel.modules.dp_group.dp_group_main import dp_group_main
from src.side_area_panel.modules.dp_group.dp_group_result import GroupValuesResult, GroupValuesStudyConfig
from tests.datasets import COL_AGE, COL_EDUCATION, COL_INCOME, MAIN
from tests.helpers import assert_data_snapshot, load_dataset, run_main


def _config(**overrides):
    base = dict(
        data_source="Auto",
        column_selector=[[COL_AGE]],
        thresholds="30, 50",
        names="",
        new_name="",
        split_side="Higher group",
    )
    base.update(overrides)
    return GroupValuesStudyConfig(**base)


CASES = [
    ("dp_group_age_auto", dict()),
    ("dp_group_age_named", dict(names="Young, Middle, Senior")),
    ("dp_group_age_lower", dict(split_side="Lower group")),
    ("dp_group_age_single_split", dict(thresholds="40")),
    ("dp_group_income_quartiles", dict(column_selector=[[COL_INCOME]], thresholds="35000, 50000, 65000")),
    # Regression: grouping a non-numeric column used to crash; it now passes the data
    # through unchanged (and flags the input).
    ("dp_group_nonnumeric_passthrough", dict(column_selector=[[COL_EDUCATION]])),
]


@pytest.mark.parametrize("name,overrides", CASES, ids=[c[0] for c in CASES])
def test_group(name, overrides):
    result = run_main(dp_group_main, GroupValuesResult, _config(**overrides), load_dataset(MAIN))
    assert_data_snapshot(result, name)
