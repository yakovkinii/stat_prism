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
"""Snapshot tests for the Reliability module.

The fixture has no dedicated item battery, so the numeric questions stand in as a
multi-item scale -- enough to exercise alpha / omega / if-item-removed deterministically.
"""

import pytest

from src.side_area_panel.modules.reliability.reliability_main import recalculate_reliability_study
from src.side_area_panel.modules.reliability.reliability_result import ReliabilityResult, ReliabilityStudyConfig
from tests.datasets import COL_AGE, COL_INCOME, COL_SATISFACTION, COL_SCORE, MAIN
from tests.helpers import assert_snapshot, load_dataset, run_main

_ITEMS = [COL_AGE, COL_INCOME, COL_SCORE, COL_SATISFACTION]


def _config(**overrides):
    base = dict(
        data_source="Auto",
        column_selector=[_ITEMS],
        correlation_type="Pearson",
        scale_name="Test scale",
        mcdonald_omega=True,
        verbal_indicators=True,
        number_columns=False,
    )
    base.update(overrides)
    return ReliabilityStudyConfig(**base)


CASES = [
    ("reliability_alpha_omega", dict()),
    ("reliability_spearman", dict(correlation_type="Spearman")),
    ("reliability_no_omega", dict(mcdonald_omega=False)),
    ("reliability_number_columns", dict(number_columns=True)),
    ("reliability_no_verbal", dict(verbal_indicators=False)),
    ("reliability_item_deleted", dict(item_deleted_table=True)),
    ("reliability_three_items", dict(column_selector=[[COL_AGE, COL_SCORE, COL_SATISFACTION]])),
]


@pytest.mark.parametrize("name,overrides", CASES, ids=[c[0] for c in CASES])
def test_reliability(name, overrides):
    result = run_main(recalculate_reliability_study, ReliabilityResult, _config(**overrides), load_dataset(MAIN))
    assert_snapshot(result, name)
