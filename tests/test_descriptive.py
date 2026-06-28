#  Copyright (c) 2023 StatPrism Team. All rights reserved.
"""Snapshot tests for the Descriptive Statistics module."""

import pytest

from src.side_area_panel.modules.descriptive.descriptive_main import recalculate_descriptive_study
from src.side_area_panel.modules.descriptive.descriptive_result import DescriptiveResult, DescriptiveStudyConfig
from tests.datasets import (
    COL_AGE,
    COL_EDUCATION,
    COL_GENDER,
    COL_GROUP,
    COL_INCOME,
    COL_REGION,
    COL_SATISFACTION,
    COL_SCORE,
    EDGE_TINY,
    MAIN,
)
from tests.helpers import assert_snapshot, load_dataset, run_main

_NUMERIC = [COL_AGE, COL_INCOME, COL_SCORE, COL_SATISFACTION]


def _config(**overrides):
    base = dict(
        data_source="Auto",
        column_selector=[[COL_AGE, COL_SCORE], []],
        extended_stats=True,
        frequency_table=False,
        show_normality=True,
        normality_test="Shapiro-Wilk",
        verbal_indicators=True,
        prose=True,
        number_columns=False,
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


CASES = [
    ("descriptive_basic", dict()),
    ("descriptive_all_numeric", dict(column_selector=[_NUMERIC, []])),
    ("descriptive_extended_off", dict(extended_stats=False)),
    ("descriptive_norm_ks", dict(normality_test="Kolmogorov-Smirnov")),
    ("descriptive_norm_ad", dict(normality_test="Anderson-Darling")),
    ("descriptive_no_normality", dict(show_normality=False)),
    ("descriptive_no_verbal", dict(verbal_indicators=False, prose=False)),
    ("descriptive_prose_only", dict(verbal_indicators=False, prose=True)),
    ("descriptive_indicators_only", dict(verbal_indicators=True, prose=False)),
    ("descriptive_number_columns", dict(column_selector=[_NUMERIC, []], number_columns=True)),
    ("descriptive_grouped", dict(column_selector=[[COL_SCORE], [COL_GROUP]])),
    ("descriptive_grouped_multi", dict(column_selector=[[COL_AGE, COL_SCORE], [COL_GROUP]])),
    ("descriptive_categorical_freq", dict(column_selector=[[COL_GENDER, COL_REGION], []], frequency_table=True)),
    ("descriptive_categorical_grouped", dict(column_selector=[[COL_REGION], [COL_GROUP]], frequency_table=True)),
    ("descriptive_plot_distribution", dict(column_selector=[[COL_SCORE], []], show_distribution=True, show_kde=True)),
    (
        "descriptive_plot_distribution_binwidth",
        dict(column_selector=[[COL_SCORE], []], show_distribution=True, bin_width="5"),
    ),
    ("descriptive_plot_box", dict(column_selector=[[COL_SCORE], []], show_box=True, mark_outliers=True)),
    ("descriptive_plot_box_grouped", dict(column_selector=[[COL_SCORE], [COL_GROUP]], show_box=True)),
    ("descriptive_plot_qq", dict(column_selector=[[COL_SCORE], []], show_qq=True)),
    ("descriptive_plot_freqbars", dict(column_selector=[[COL_REGION], []], show_frequency_bars=True)),
    ("descriptive_plot_pie", dict(column_selector=[[COL_REGION], []], show_pie=True)),
]


@pytest.mark.parametrize("name,overrides", CASES, ids=[c[0] for c in CASES])
def test_descriptive(name, overrides):
    result = run_main(recalculate_descriptive_study, DescriptiveResult, _config(**overrides), load_dataset(MAIN))
    assert_snapshot(result, name)


def test_descriptive_tiny():
    # Edge: very small sample (n=4).
    result = run_main(
        recalculate_descriptive_study,
        DescriptiveResult,
        _config(column_selector=[[COL_SCORE], []]),
        load_dataset(EDGE_TINY),
    )
    assert_snapshot(result, "descriptive_tiny")


def test_descriptive_ordinal_pie():
    # Education promoted to ordinal -> ordinal summary + pie in defined order.
    data = load_dataset(MAIN, ordinal={COL_EDUCATION: ["High school", "Bachelor", "Master", "PhD"]})
    result = run_main(
        recalculate_descriptive_study,
        DescriptiveResult,
        _config(column_selector=[[COL_EDUCATION], []], show_pie=True, frequency_table=True),
        data,
    )
    assert_snapshot(result, "descriptive_ordinal_pie")
