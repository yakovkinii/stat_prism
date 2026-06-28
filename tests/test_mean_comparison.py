#  Copyright (c) 2023 StatPrism Team. All rights reserved.
"""Snapshot tests for the T-test / ANOVA (mean comparison) module."""

import pytest

from src.side_area_panel.modules.mean_comparison.constant import (
    AssumptionChecksInGrouping,
    MeanComparisonMethod,
    MissingValuesInGrouping,
)
from src.side_area_panel.modules.mean_comparison.mean_comparison_main import recalculate_mean_comparison_study
from src.side_area_panel.modules.mean_comparison.mean_comparison_result import (
    MeanComparisonResult,
    MeanComparisonStudyConfig,
)
from tests.datasets import COL_AGE, COL_GROUP, COL_PASSED, COL_SCORE, MAIN
from tests.helpers import assert_snapshot, load_dataset, run_main

_HOM = MeanComparisonMethod.HOMOGENEOUS.value
_WELCH = MeanComparisonMethod.INHOMOGENEOUS.value
_NONPARAM = MeanComparisonMethod.NON_PARAMETRIC.value
_AUTO = MeanComparisonMethod.AUTO.value
_SKIP = MissingValuesInGrouping.SKIP.value
_CHK_AUTO = AssumptionChecksInGrouping.AUTO.value
_CHK_ALWAYS = AssumptionChecksInGrouping.ALWAYS.value

# Two groups (Yes/No) -> t-test family; three groups (A/B/C) -> ANOVA family.
_TWO = [[COL_SCORE], [COL_PASSED]]
_THREE = [[COL_SCORE], [COL_GROUP]]


def _config(**overrides):
    base = dict(
        data_source="Auto",
        column_selector=_TWO,
        method=_HOM,
        grouping_missing=_SKIP,
        assumption_checks=_CHK_AUTO,
        effect_size=True,
        verbal_indicators=True,
        confidence_intervals=True,
        number_columns=False,
        plots=False,
    )
    base.update(overrides)
    return MeanComparisonStudyConfig(**base)


CASES = [
    ("mean_comparison_ttest", dict()),
    ("mean_comparison_ttest_welch", dict(method=_WELCH)),
    ("mean_comparison_ttest_nonparam", dict(method=_NONPARAM)),
    ("mean_comparison_ttest_auto", dict(method=_AUTO)),
    ("mean_comparison_ttest_no_effect", dict(effect_size=False)),
    ("mean_comparison_ttest_no_ci", dict(confidence_intervals=False)),
    ("mean_comparison_ttest_assumptions_always", dict(assumption_checks=_CHK_ALWAYS)),
    ("mean_comparison_ttest_multi_dv", dict(column_selector=[[COL_SCORE, COL_AGE], [COL_PASSED]])),
    ("mean_comparison_anova", dict(column_selector=_THREE)),
    ("mean_comparison_anova_welch", dict(column_selector=_THREE, method=_WELCH)),
    ("mean_comparison_anova_nonparam", dict(column_selector=_THREE, method=_NONPARAM)),
    ("mean_comparison_anova_auto", dict(column_selector=_THREE, method=_AUTO)),
    (
        "mean_comparison_anova_number_columns",
        dict(column_selector=[[COL_SCORE, COL_AGE], [COL_GROUP]], number_columns=True),
    ),
]


@pytest.mark.parametrize("name,overrides", CASES, ids=[c[0] for c in CASES])
def test_mean_comparison(name, overrides):
    result = run_main(recalculate_mean_comparison_study, MeanComparisonResult, _config(**overrides), load_dataset(MAIN))
    assert_snapshot(result, name)
