#  Copyright (c) 2023 StatPrism Team. All rights reserved.
"""Snapshot tests for the Descriptive Statistics module."""

import pandas as pd

from src.side_area_panel.modules.descriptive.descriptive_main import (
    recalculate_descriptive_study,
)
from src.side_area_panel.modules.descriptive.descriptive_result import (
    DescriptiveResult,
    DescriptiveStudyConfig,
)
from tests.helpers import assert_snapshot, make_data, run_main

DF = pd.DataFrame(
    {
        "age": [23, 31, 29, 41, 35, 28, 52, 38, 26, 44],
        "score": [5.5, 6.1, 5.9, 7.2, 6.8, 5.1, 8.0, 6.5, 5.3, 7.1],
        "group": ["A", "B", "A", "B", "A", "B", "A", "B", "A", "B"],
    }
)


def _config(**overrides):
    base = dict(
        data_source="Auto",
        column_selector=[["age", "score"], []],
        extended_stats=True,
        frequency_table=False,
        show_normality=True,
        normality_test="Shapiro-Wilk",
        verbal_indicators=True,
        number_columns=False,
        # Plots off: tables-only keeps these first benchmarks small and stable.
        show_distribution=False,
        show_box=False,
        mark_outliers=False,
        show_frequency_bars=False,
        show_pie=False,
        show_qq=False,
        show_kde=False,
        bin_width="",
        bin_reference="",
        kde_smoothing="",
    )
    base.update(overrides)
    return DescriptiveStudyConfig(**base)


def test_descriptive_basic():
    result = run_main(
        recalculate_descriptive_study,
        DescriptiveResult,
        _config(),
        make_data(DF),
    )
    assert_snapshot(result, "descriptive_basic")


def test_descriptive_grouped():
    result = run_main(
        recalculate_descriptive_study,
        DescriptiveResult,
        _config(column_selector=[["score"], ["group"]]),
        make_data(DF),
    )
    assert_snapshot(result, "descriptive_grouped")
