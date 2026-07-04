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
"""Snapshot tests for the Split Multi-Select DP module.

Splits the Google-Forms checkbox column (comma-separated options) into one 0/1
indicator column per option. DP module -> snapshot the transformed data.
"""

import pytest

from src.side_area_panel.modules.dp_split_multiselect.dp_split_multiselect_main import dp_split_multiselect_main
from src.side_area_panel.modules.dp_split_multiselect.dp_split_multiselect_result import (
    SplitMultiSelectResult,
    SplitMultiSelectStudyConfig,
)
from tests.datasets import COL_FEATURES, MAIN
from tests.helpers import assert_data_snapshot, load_dataset, run_main


def _config(**overrides):
    base = dict(
        data_source="Auto",
        column_selector=[[COL_FEATURES]],
        delimiter=",",
        prefix="",
    )
    base.update(overrides)
    return SplitMultiSelectStudyConfig(**base)


CASES = [
    ("dp_split_multiselect_features", dict()),
    ("dp_split_multiselect_prefix", dict(prefix="feat_")),
    # Wrong delimiter -> nothing matches -> pass-through (original data unchanged).
    ("dp_split_multiselect_no_match", dict(delimiter=";")),
]


@pytest.mark.parametrize("name,overrides", CASES, ids=[c[0] for c in CASES])
def test_split_multiselect(name, overrides):
    result = run_main(dp_split_multiselect_main, SplitMultiSelectResult, _config(**overrides), load_dataset(MAIN))
    assert_data_snapshot(result, name)
