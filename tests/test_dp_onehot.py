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
"""Snapshot tests for the Encode Categories (one-hot) DP module.

DP modules produce a transformed ``Data`` (``result.data``), so these use
``assert_data_snapshot`` -- the resulting dataframe + column metadata is rendered to
HTML and compared like analysis snapshots.
"""

import pytest

from src.side_area_panel.modules.dp_onehot.dp_onehot_main import dp_onehot_main
from src.side_area_panel.modules.dp_onehot.dp_onehot_result import OneHotResult, OneHotStudyConfig
from tests.datasets import COL_EDUCATION, COL_GENDER, COL_REGION, MAIN
from tests.helpers import assert_data_snapshot, load_dataset, run_main


def _config(**overrides):
    base = dict(
        data_source="Auto",
        column_selector=[[COL_REGION]],
        drop_reference=True,
        reference="",
    )
    base.update(overrides)
    return OneHotStudyConfig(**base)


CASES = [
    ("dp_onehot_region_drop", dict()),
    ("dp_onehot_region_keep", dict(drop_reference=False)),
    ("dp_onehot_region_reference", dict(reference="North")),
    ("dp_onehot_gender_drop", dict(column_selector=[[COL_GENDER]])),
    ("dp_onehot_education_keep", dict(column_selector=[[COL_EDUCATION]], drop_reference=False)),
]


@pytest.mark.parametrize("name,overrides", CASES, ids=[c[0] for c in CASES])
def test_onehot(name, overrides):
    result = run_main(dp_onehot_main, OneHotResult, _config(**overrides), load_dataset(MAIN))
    assert_data_snapshot(result, name)
