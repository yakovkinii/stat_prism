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
"""Snapshot tests for the Power Analysis module (needs no input data)."""

import pytest

from src.side_area_panel.modules.power_analysis.power_analysis_main import recalculate_power_analysis_study
from src.side_area_panel.modules.power_analysis.power_analysis_result import (
    PowerAnalysisResult,
    PowerAnalysisStudyConfig,
)
from tests.datasets import MAIN
from tests.helpers import assert_snapshot, load_dataset, run_main

_TWO = "Two-sample t-test"
_PAIRED = "Paired / one-sample t-test"
_ANOVA = "One-way ANOVA"
_CORR = "Correlation"


def _config(**overrides):
    base = dict(
        test_type=_TWO,
        solve_for="Sample size",
        alpha="0.05",
        power="0.80",
        effect_size="0.5",
        sample_size="30",
        n_groups="3",
        tails="Two-sided",
    )
    base.update(overrides)
    return PowerAnalysisStudyConfig(**base)


CASES = [
    ("power_ttest_sample_size", dict()),
    ("power_ttest_power", dict(solve_for="Power")),
    ("power_ttest_effect_size", dict(solve_for="Effect size")),
    ("power_ttest_one_sided", dict(tails="One-sided")),
    ("power_paired_sample_size", dict(test_type=_PAIRED)),
    ("power_paired_power", dict(test_type=_PAIRED, solve_for="Power")),
    ("power_anova_sample_size", dict(test_type=_ANOVA)),
    ("power_anova_power", dict(test_type=_ANOVA, solve_for="Power")),
    ("power_anova_effect_size", dict(test_type=_ANOVA, solve_for="Effect size")),
    ("power_anova_four_groups", dict(test_type=_ANOVA, n_groups="4")),
    ("power_corr_sample_size", dict(test_type=_CORR, effect_size="0.3")),
    ("power_corr_power", dict(test_type=_CORR, solve_for="Power", effect_size="0.3")),
    ("power_corr_effect_size", dict(test_type=_CORR, solve_for="Effect size")),
]


@pytest.mark.parametrize("name,overrides", CASES, ids=[c[0] for c in CASES])
def test_power_analysis(name, overrides):
    result = run_main(
        recalculate_power_analysis_study,
        PowerAnalysisResult,
        _config(**overrides),
        load_dataset(MAIN),  # unused by this module, but run_main expects a Data
    )
    assert_snapshot(result, name)
