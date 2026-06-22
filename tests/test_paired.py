#  Copyright (c) 2023 StatPrism Team. All rights reserved.
"""Snapshot tests for the Paired / Repeated Measures module.

The fixture has no true paired conditions, so numeric questions stand in as the
conditions -- enough to exercise the paired / repeated-measures computation.
"""

import pytest

from src.side_area_panel.modules.paired.constant import (
    PairedAssumptionChecks,
    PairedMethod,
)
from src.side_area_panel.modules.paired.paired_main import recalculate_paired_study
from src.side_area_panel.modules.paired.paired_result import (
    PairedResult,
    PairedStudyConfig,
)
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
