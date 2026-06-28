#  Copyright (c) 2023 StatPrism Team. All rights reserved.
"""Snapshot tests for the Multiple Response module.

The natural two-step pipeline: Split Multi-Select turns the checkbox column into 0/1
indicators, then Multiple Response summarises them. The split output is fed straight
in as the data source for the second step.
"""

import pytest

from src.side_area_panel.modules.dp_split_multiselect.dp_split_multiselect_main import dp_split_multiselect_main
from src.side_area_panel.modules.dp_split_multiselect.dp_split_multiselect_result import (
    SplitMultiSelectResult,
    SplitMultiSelectStudyConfig,
)
from src.side_area_panel.modules.multiple_response.multiple_response_main import recalculate_multiple_response_study
from src.side_area_panel.modules.multiple_response.multiple_response_result import (
    MultipleResponseResult,
    MultipleResponseStudyConfig,
)
from tests.datasets import COL_FEATURES, FEATURE_OPTIONS, MAIN
from tests.helpers import assert_snapshot, load_dataset, run_main


def _split_indicators():
    """Run Split Multi-Select and return (split_data, indicator_column_names)."""
    split = run_main(
        dp_split_multiselect_main,
        SplitMultiSelectResult,
        SplitMultiSelectStudyConfig(
            data_source="Auto",
            column_selector=[[COL_FEATURES]],
            delimiter=",",
            prefix="",
        ),
        load_dataset(MAIN),
    )
    indicators = [c for c in split.data.column_names() if c in FEATURE_OPTIONS]
    return split.data, indicators


@pytest.mark.parametrize(
    "name,show_chart,verbal",
    [
        ("multiple_response_features", False, False),
        ("multiple_response_features_chart", True, False),
        ("multiple_response_features_verbal", False, True),
    ],
    ids=["no_chart", "chart", "verbal"],
)
def test_multiple_response(name, show_chart, verbal):
    data, indicators = _split_indicators()
    result = run_main(
        recalculate_multiple_response_study,
        MultipleResponseResult,
        MultipleResponseStudyConfig(
            data_source="Auto",
            column_selector=[indicators],
            show_chart=show_chart,
            verbal_indicators=verbal,
        ),
        data,
    )
    assert_snapshot(result, name)
