#  Copyright (c) 2023 StatPrism Team. All rights reserved.
"""Snapshot tests for the Correlation module."""

import pandas as pd

from src.side_area_panel.modules.correlation.correlation_main import (
    recalculate_correlation_study,
)
from src.side_area_panel.modules.correlation.correlation_result import (
    CorrelationResult,
    CorrelationStudyConfig,
)
from tests.helpers import assert_snapshot, make_data, run_main

DF = pd.DataFrame(
    {
        "age": [23, 31, 29, 41, 35, 28, 52, 38, 26, 44],
        "score": [5.5, 6.1, 5.9, 7.2, 6.8, 5.1, 8.0, 6.5, 5.3, 7.1],
        "extra": [10, 12, 11, 15, 14, 9, 18, 13, 10, 16],
    }
)


def _config(**overrides):
    base = dict(
        data_source="Auto",
        # [primary set, control/partial set, second (cross) set]
        column_selector=[["age", "score", "extra"], [], []],
        correlation_type="Pearson",
        compact=False,
        generate_heatmap=False,
        generate_plots=False,
        report_only_significant=False,
        confidence_intervals=True,
        number_columns=False,
    )
    base.update(overrides)
    return CorrelationStudyConfig(**base)


def test_correlation_pearson():
    result = run_main(
        recalculate_correlation_study,
        CorrelationResult,
        _config(),
        make_data(DF),
    )
    assert_snapshot(result, "correlation_pearson")


def test_correlation_spearman():
    result = run_main(
        recalculate_correlation_study,
        CorrelationResult,
        _config(correlation_type="Spearman"),
        make_data(DF),
    )
    assert_snapshot(result, "correlation_spearman")


def test_correlation_pearson_heatmap():
    # Exercises a plot path: the heatmap is embedded inline as a base64 PNG, so the
    # snapshot (and the review tool) carry the rendered image too.
    result = run_main(
        recalculate_correlation_study,
        CorrelationResult,
        _config(generate_heatmap=True),
        make_data(DF),
    )
    assert_snapshot(result, "correlation_pearson_heatmap")
