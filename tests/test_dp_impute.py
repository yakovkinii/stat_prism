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
