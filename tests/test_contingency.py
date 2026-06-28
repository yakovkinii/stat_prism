#  Copyright (c) 2023 StatPrism Team. All rights reserved.
"""Snapshot tests for the Contingency Table module."""

import pytest

from src.side_area_panel.modules.contingency.contingency_main import recalculate_contingency_study
from src.side_area_panel.modules.contingency.contingency_result import ContingencyResult, ContingencyStudyConfig
from tests.datasets import COL_EDUCATION, COL_GENDER, COL_GROUP, COL_PASSED, COL_REGION, MAIN
from tests.helpers import assert_snapshot, load_dataset, run_main


def _config(**overrides):
    base = dict(
        data_source="Auto",
        column_selector=[[COL_REGION], [COL_GROUP]],
        continuity_correction=False,
        effect_size=True,
        verbal_indicators=True,
        mcnemar=False,
        plots=False,
    )
    base.update(overrides)
    return ContingencyStudyConfig(**base)


CASES = [
    ("contingency_region_group", dict()),
    ("contingency_gender_passed", dict(column_selector=[[COL_GENDER], [COL_PASSED]])),
    ("contingency_education_group", dict(column_selector=[[COL_EDUCATION], [COL_GROUP]])),
    ("contingency_region_passed", dict(column_selector=[[COL_REGION], [COL_PASSED]])),
    ("contingency_no_effect", dict(effect_size=False)),
    ("contingency_no_verbal", dict(verbal_indicators=False)),
    ("contingency_with_plot", dict(plots=True)),
    ("contingency_continuity", dict(continuity_correction=True)),
]


@pytest.mark.parametrize("name,overrides", CASES, ids=[c[0] for c in CASES])
def test_contingency(name, overrides):
    result = run_main(recalculate_contingency_study, ContingencyResult, _config(**overrides), load_dataset(MAIN))
    assert_snapshot(result, name)
