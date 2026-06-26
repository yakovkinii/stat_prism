#  Copyright (c) 2023 StatPrism Team. All rights reserved.
"""Snapshot tests for the Exploratory Factor Analysis module.

Uses the numeric questions as the variable set (no dedicated item battery exists).
"""

import pytest

from src.side_area_panel.modules.exploratory_factor_analysis.exploratory_factor_analysis_main import (
    recalculate_factor_analysis_study,
)
from src.side_area_panel.modules.exploratory_factor_analysis.exploratory_factor_analysis_result import (
    ExtractionMethod,
    FactorAnalysisResult,
    FactorAnalysisStudyConfig,
    RotationType,
)
from tests.datasets import COL_AGE, COL_INCOME, COL_SATISFACTION, COL_SCORE, MAIN
from tests.helpers import assert_snapshot, load_dataset, run_main

_ITEMS = [COL_AGE, COL_INCOME, COL_SCORE, COL_SATISFACTION]
_MINRES = ExtractionMethod.MINRES.value
_PAF = ExtractionMethod.PRINCIPAL.value


def _config(**overrides):
    base = dict(
        data_source="Auto",
        column_selector=[_ITEMS],
        method=_MINRES,
        rotation=RotationType.VARIMAX.value,
        n_factors=2,
        kaiser_normalization=True,
        plots=False,
        number_columns=False,
    )
    base.update(overrides)
    return FactorAnalysisStudyConfig(**base)


CASES = [
    ("efa_minres_varimax", dict()),
    ("efa_minres_none", dict(rotation=RotationType.NONE.value)),
    ("efa_minres_promax", dict(rotation=RotationType.PROMAX.value)),
    ("efa_minres_oblimin", dict(rotation=RotationType.OBLIMIN.value)),
    ("efa_minres_quartimax", dict(rotation=RotationType.QUARTIMAX.value)),
    ("efa_paf_varimax", dict(method=_PAF)),
    ("efa_minres_one_factor", dict(n_factors=1)),
    ("efa_minres_three_factors", dict(n_factors=3)),
    ("efa_number_columns", dict(number_columns=True)),
    ("efa_verbal", dict(verbal_indicators=True)),
]


@pytest.mark.parametrize("name,overrides", CASES, ids=[c[0] for c in CASES])
def test_efa(name, overrides):
    result = run_main(recalculate_factor_analysis_study, FactorAnalysisResult, _config(**overrides), load_dataset(MAIN))
    assert_snapshot(result, name)
