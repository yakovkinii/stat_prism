#  Copyright (c) 2023 StatPrism Team. All rights reserved.
"""Snapshot tests for the Correlation module."""

import pytest

from src.side_area_panel.modules.correlation.correlation_main import recalculate_correlation_study
from src.side_area_panel.modules.correlation.correlation_result import CorrelationResult, CorrelationStudyConfig
from tests.datasets import (
    COL_AGE,
    COL_CONSTANT,
    COL_INCOME,
    COL_SATISFACTION,
    COL_SCORE,
    COL_VARYING,
    EDGE_CONSTANT,
    MAIN,
)
from tests.helpers import assert_snapshot, load_dataset, run_main

_THREE = [COL_AGE, COL_INCOME, COL_SCORE]
_FOUR = [COL_AGE, COL_INCOME, COL_SCORE, COL_SATISFACTION]


def _config(**overrides):
    base = dict(
        data_source="Auto",
        column_selector=[_THREE, [], []],
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


CASES = [
    ("correlation_pearson", dict()),
    ("correlation_spearman", dict(correlation_type="Spearman")),
    ("correlation_kendall", dict(correlation_type="Kendall")),
    ("correlation_pearson_compact", dict(compact=True)),
    ("correlation_spearman_compact", dict(correlation_type="Spearman", compact=True)),
    ("correlation_no_ci", dict(confidence_intervals=False)),
    ("correlation_four_vars", dict(column_selector=[_FOUR, [], []])),
    ("correlation_number_columns", dict(column_selector=[_FOUR, [], []], number_columns=True)),
    ("correlation_only_significant", dict(column_selector=[_FOUR, [], []], report_only_significant=True)),
    ("correlation_partial_pearson", dict(column_selector=[[COL_AGE, COL_SCORE], [COL_INCOME], []])),
    (
        "correlation_partial_spearman",
        dict(correlation_type="Spearman", column_selector=[[COL_AGE, COL_SCORE], [COL_INCOME], []]),
    ),
    ("correlation_cross", dict(column_selector=[[COL_AGE, COL_SCORE], [], [COL_INCOME, COL_SATISFACTION]])),
    ("correlation_heatmap", dict(generate_heatmap=True)),
]


@pytest.mark.parametrize("name,overrides", CASES, ids=[c[0] for c in CASES])
def test_correlation(name, overrides):
    result = run_main(recalculate_correlation_study, CorrelationResult, _config(**overrides), load_dataset(MAIN))
    assert_snapshot(result, name)


def test_correlation_constant_column():
    # Edge: a zero-variance column -> correlation undefined for that pair.
    result = run_main(
        recalculate_correlation_study,
        CorrelationResult,
        _config(column_selector=[[COL_CONSTANT, COL_VARYING], [], []]),
        load_dataset(EDGE_CONSTANT),
    )
    assert_snapshot(result, "correlation_constant_column")
