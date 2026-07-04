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
"""Snapshot tests for the Paired / Repeated Measures module.

The fixture has no true paired conditions, so numeric questions stand in as the
conditions -- enough to exercise the paired / repeated-measures computation.
"""

import pytest

from src.side_area_panel.modules.paired.constant import PairedAssumptionChecks, PairedMethod
from src.side_area_panel.modules.paired.paired_main import recalculate_paired_study
from src.side_area_panel.modules.paired.paired_result import PairedResult, PairedStudyConfig
from tests.datasets import COL_AGE, COL_INCOME, COL_SCORE, MAIN
from tests.helpers import assert_snapshot, load_dataset, run_main

_PARAM = PairedMethod.PARAMETRIC.value
_NONPARAM = PairedMethod.NON_PARAMETRIC.value
_CHK_AUTO = PairedAssumptionChecks.AUTO.value
_CHK_ALWAYS = PairedAssumptionChecks.ALWAYS.value

_TWO = [[COL_AGE, COL_SCORE]]
_THREE = [[COL_AGE, COL_SCORE, COL_INCOME]]


def _config(**overrides):
    base = dict(
        data_source="Auto",
        column_selector=_TWO,
        method=_PARAM,
        assumption_checks=_CHK_AUTO,
        effect_size=True,
        verbal_indicators=True,
        number_columns=False,
        plots=False,
    )
    base.update(overrides)
    return PairedStudyConfig(**base)


CASES = [
    ("paired_param_two", dict()),
    ("paired_nonparam_two", dict(method=_NONPARAM)),
    ("paired_param_three", dict(column_selector=_THREE)),
    ("paired_nonparam_three", dict(column_selector=_THREE, method=_NONPARAM)),
    ("paired_no_effect", dict(effect_size=False)),
    ("paired_assumptions_always", dict(assumption_checks=_CHK_ALWAYS)),
    ("paired_number_columns", dict(column_selector=_THREE, number_columns=True)),
]


@pytest.mark.parametrize("name,overrides", CASES, ids=[c[0] for c in CASES])
def test_paired(name, overrides):
    result = run_main(recalculate_paired_study, PairedResult, _config(**overrides), load_dataset(MAIN))
    assert_snapshot(result, name)
