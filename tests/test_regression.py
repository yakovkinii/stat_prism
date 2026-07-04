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
"""Snapshot tests for the Regression module."""

import pytest

from src.side_area_panel.modules.regression.regression_main import recalculate_regression_study
from src.side_area_panel.modules.regression.regression_result import RegressionResult, RegressionStudyConfig
from tests.datasets import COL_AGE, COL_INCOME, COL_SATISFACTION, COL_SCORE, MAIN
from tests.helpers import assert_snapshot, load_dataset, run_main


def _config(**overrides):
    base = dict(
        data_source="Auto",
        # [dependent, independent(s), moderator, mediator]
        column_selector=[[COL_SCORE], [COL_AGE, COL_INCOME], [], []],
        model_type=None,  # defaults to linear OLS
        standardized=True,
        verbal_indicators=True,
        diagnostics=True,
        plots=False,
    )
    base.update(overrides)
    return RegressionStudyConfig(**base)


CASES = [
    ("regression_linear", dict()),
    ("regression_single_predictor", dict(column_selector=[[COL_SCORE], [COL_AGE], [], []])),
    (
        "regression_three_predictors",
        dict(column_selector=[[COL_SCORE], [COL_AGE, COL_INCOME, COL_SATISFACTION], [], []]),
    ),
    ("regression_unstandardized", dict(standardized=False)),
    ("regression_no_diagnostics", dict(diagnostics=False)),
    ("regression_no_verbal", dict(verbal_indicators=False)),
    ("regression_with_plot", dict(column_selector=[[COL_SCORE], [COL_AGE], [], []], plots=True)),
    ("regression_moderation", dict(column_selector=[[COL_SCORE], [COL_AGE], [COL_INCOME], []])),
    ("regression_mediation", dict(column_selector=[[COL_SCORE], [COL_AGE], [], [COL_INCOME]])),
]


@pytest.mark.parametrize("name,overrides", CASES, ids=[c[0] for c in CASES])
def test_regression(name, overrides):
    result = run_main(recalculate_regression_study, RegressionResult, _config(**overrides), load_dataset(MAIN))
    assert_snapshot(result, name)
