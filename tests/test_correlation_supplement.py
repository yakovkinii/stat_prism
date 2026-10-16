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

"""Headless coverage of every branch of the Correlation module via its numeric supplement.

The module attaches the raw numbers behind its result table with
``html_table.add_numeric_supplement(...)`` during a fresh recompute. These tests drive
``recalculate_correlation_study`` headlessly (offscreen QApplication from conftest, DATA_MANAGER
monkeypatched to a test dataset), fetch the supplement from the rendered result, and assert it
carries exactly what the estimator produced -- for each coefficient, layout (compact / full),
partial, cross and error branch.
"""

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from src.common.constant import ColumnType
from src.data.data import Data
from src.pyside_ext.styling import Style

# Load registry before correlation_result so their mutual import resolves (registry re-imports
# CorrelationResult from correlation_result); importing the correlation math module first would pull
# correlation_result mid-initialisation and raise ImportError.
import src.side_area_panel.modules.common.result.registry  # noqa: F401,E402  (import-order guard)
from src.side_area_panel.modules.common.mathematics.correlation.correlation import (
    calculate_correlations,
    calculate_cross_correlations,
    calculate_partial_correlations,
    calculate_partial_cross_correlations,
)
from src.side_area_panel.modules.correlation import correlation_main
from src.side_area_panel.modules.correlation.correlation_main import recalculate_correlation_study
from src.side_area_panel.modules.correlation.correlation_result import (
    CorrelationResult,
    CorrelationStudyConfig,
    CorrelationType,
)

TYPE_KEYS = {
    "Pearson": CorrelationType.PEARSON,
    "Spearman": CorrelationType.SPEARMAN,
    "Kendall": CorrelationType.KENDALL,
    "Kendall tau c": CorrelationType.KENDALL_C,
    "Phi": CorrelationType.PHI,
    "Tetrachoric": CorrelationType.TETRACHORIC,
    "Polychoric": CorrelationType.POLYCHORIC,
}
BINARY_KEYS = {"Phi", "Tetrachoric"}


# --------------------------------------------------------------------------------------------------
# Test data (deterministic, correlated, no constant columns)
# --------------------------------------------------------------------------------------------------
def _likert_frame() -> pd.DataFrame:
    rng = np.random.default_rng(12345)
    n = 80
    latent = rng.normal(size=n)

    def likert(load):
        x = load * latent + rng.normal(scale=0.8, size=n)
        ranks = pd.Series(x).rank(method="first").to_numpy()
        return (((ranks - 1) * 5 // n) + 1).astype(int)  # 1..5, every category present

    return pd.DataFrame(
        {"v1": likert(1.0), "v2": likert(0.8), "v3": likert(-0.6), "v4": likert(0.3), "ctrl": likert(0.5)}
    )


def _binary_frame() -> pd.DataFrame:
    rng = np.random.default_rng(777)
    n = 80
    latent = rng.normal(size=n)

    def binary(load):
        x = load * latent + rng.normal(scale=0.8, size=n)
        return (x > np.median(x)).astype(int)

    return pd.DataFrame({"b1": binary(1.0), "b2": binary(0.7), "b3": binary(-0.5)})


def _data(frame: pd.DataFrame) -> Data:
    return Data.initialize_from_dataframe(frame)


def _data_for(type_key: str):
    if type_key in BINARY_KEYS:
        return _data(_binary_frame()), ["b1", "b2", "b3"]
    return _data(_likert_frame()), ["v1", "v2", "v3"]


# --------------------------------------------------------------------------------------------------
# Driving the module headlessly
# --------------------------------------------------------------------------------------------------
def _run(monkeypatch, data, selected, controls=None, second=None, **cfg_kwargs) -> CorrelationResult:
    monkeypatch.setattr(correlation_main.DATA_MANAGER, "get_data_from_data_label", lambda *a, **k: data)
    cfg = CorrelationStudyConfig(
        data_source="Auto",
        column_selector=[list(selected), list(controls or []), list(second or [])],
        **cfg_kwargs,
    )
    result = CorrelationResult(unique_id=1, settings_panel_index=0, config=cfg)
    return recalculate_correlation_study(None, result, lambda _p: None)


def _supplement(result: CorrelationResult) -> dict:
    supplements = result.numeric_supplements()
    assert len(supplements) == 1, f"expected exactly one numeric supplement, got {len(supplements)}"
    return supplements[0]


def _prepare_df(data: Data, cols, kind: CorrelationType) -> pd.DataFrame:
    """Reproduce the module's dataframe prep so the expected matrices use the same inputs."""
    if kind == CorrelationType.PEARSON:
        df, _ = data.get_numeric_face_dataframe(list(cols))
        return df
    return data.get_dataframe(columns=list(cols), map_ordinal=True)


def _assert_matrix(actual, expected):
    assert_frame_equal(actual.astype(float), expected.astype(float), check_dtype=False)


# --------------------------------------------------------------------------------------------------
# Every coefficient, compact and full
# --------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("type_key", list(TYPE_KEYS))
@pytest.mark.parametrize("compact", [True, False])
def test_basic_supplement_matches_estimator(monkeypatch, type_key, compact):
    kind = TYPE_KEYS[type_key]
    data, selected = _data_for(type_key)

    result = _run(monkeypatch, data, selected, correlation_type=type_key, compact=compact)

    assert result.error_message == ""
    supplement = _supplement(result)
    assert supplement["columns"] == selected
    assert supplement["kind"] == kind
    if compact:
        assert set(supplement) == {"columns", "correlation_matrix", "p_matrix", "kind", "numbering"}
    else:
        assert set(supplement) == {
            "columns",
            "correlation_matrix",
            "p_matrix",
            "df_matrix",
            "kind",
            "ci_matrix",
            "numbering",
        }
        assert supplement["ci_matrix"] is None  # off unless confidence_intervals is set

    df = _prepare_df(data, selected, kind)
    expected_corr, expected_p, _expected_df = calculate_correlations(df[selected], kind)
    _assert_matrix(supplement["correlation_matrix"], expected_corr)
    _assert_matrix(supplement["p_matrix"], expected_p)
    assert result.get_html()


# --------------------------------------------------------------------------------------------------
# Partial correlation (Pearson / Spearman only) + the method-error guard
# --------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("type_key", ["Pearson", "Spearman"])
@pytest.mark.parametrize("compact", [True, False])
def test_partial_supplement_matches_estimator(monkeypatch, type_key, compact):
    kind = TYPE_KEYS[type_key]
    data = _data(_likert_frame())
    selected, controls = ["v1", "v2", "v3"], ["ctrl"]

    result = _run(
        monkeypatch,
        data,
        selected,
        controls=controls,
        correlation_type=type_key,
        compact=compact,
        interpretation="Full",  # also exercises the verbal report + partial-note branch
    )

    assert result.error_message == ""
    supplement = _supplement(result)
    df = _prepare_df(data, selected + controls, kind)
    expected_corr, _p, _dfm = calculate_partial_correlations(df, selected, controls, kind)
    _assert_matrix(supplement["correlation_matrix"], expected_corr)
    assert result.get_html()


def test_partial_with_unsupported_type_errors(monkeypatch):
    data = _data(_likert_frame())
    result = _run(monkeypatch, data, ["v1", "v2"], controls=["ctrl"], correlation_type="Kendall")
    assert Style.Color.Danger.value in result.get_html()  # correlation.partial.method_error is rendered
    assert result.numeric_supplements() == []


# --------------------------------------------------------------------------------------------------
# Confidence intervals (full layout only)
# --------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("ci", [True, False])
def test_confidence_intervals_in_supplement(monkeypatch, ci):
    data = _data(_likert_frame())
    result = _run(
        monkeypatch,
        data,
        ["v1", "v2", "v3"],
        correlation_type="Pearson",
        compact=False,
        confidence_intervals=ci,
    )
    supplement = _supplement(result)
    if ci:
        assert isinstance(supplement["ci_matrix"], pd.DataFrame)
    else:
        assert supplement["ci_matrix"] is None


# --------------------------------------------------------------------------------------------------
# Cross (two-set) correlation: non-partial compact/full, partial, and the cross-min guard
# --------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("compact", [True, False])
def test_cross_supplement_matches_estimator(monkeypatch, compact):
    data = _data(_likert_frame())
    rows, cols = ["v1", "v2"], ["v3", "v4"]

    result = _run(
        monkeypatch,
        data,
        rows,
        second=cols,
        correlation_type="Pearson",
        compact=compact,
        interpretation="Full",
    )

    assert result.error_message == ""
    supplement = _supplement(result)
    assert supplement["rows"] == rows
    assert supplement["cols"] == cols
    df = _prepare_df(data, rows + cols, CorrelationType.PEARSON)
    expected_corr, _p, _dfm = calculate_cross_correlations(df, rows, cols, CorrelationType.PEARSON)
    _assert_matrix(supplement["correlation_matrix"], expected_corr)
    assert result.get_html()


def test_cross_partial_supplement_matches_estimator(monkeypatch):
    data = _data(_likert_frame())
    rows, cols, controls = ["v1", "v2"], ["v3"], ["ctrl"]

    result = _run(
        monkeypatch,
        data,
        rows,
        controls=controls,
        second=cols,
        correlation_type="Spearman",
        compact=False,
    )

    assert result.error_message == ""
    supplement = _supplement(result)
    df = _prepare_df(data, rows + cols + controls, CorrelationType.SPEARMAN)
    expected_corr, _p, _dfm = calculate_partial_cross_correlations(
        df, rows, cols, controls, CorrelationType.SPEARMAN
    )
    _assert_matrix(supplement["correlation_matrix"], expected_corr)


def test_cross_requires_both_sets(monkeypatch):
    data = _data(_likert_frame())
    # A non-empty second set makes it a cross; an empty first set trips the cross-min guard.
    result = _run(monkeypatch, data, [], second=["v1"], correlation_type="Pearson")
    assert Style.Color.Danger.value in result.get_html()  # correlation.error.cross_min is rendered
    assert result.numeric_supplements() == []


# --------------------------------------------------------------------------------------------------
# Validation guard: too few variables
# --------------------------------------------------------------------------------------------------
def test_too_few_variables_errors(monkeypatch):
    data = _data(_likert_frame())
    result = _run(monkeypatch, data, ["v1"], correlation_type="Pearson")
    assert Style.Color.Danger.value in result.get_html()  # correlation.error.min_variables is rendered
    assert result.numeric_supplements() == []


# --------------------------------------------------------------------------------------------------
# Heatmap + pairwise plots + verbal report + numbering all on at once
# --------------------------------------------------------------------------------------------------
def test_extras_branches_render(monkeypatch):
    data = _data(_likert_frame())
    result = _run(
        monkeypatch,
        data,
        ["v1", "v2", "v3"],
        correlation_type="Pearson",
        compact=False,
        generate_heatmap=True,
        generate_plots=True,
        report_only_significant=False,  # draw every pairwise plot
        number_columns=True,
        interpretation="Full",
        confidence_intervals=True,
    )
    assert result.error_message == ""
    supplement = _supplement(result)
    assert isinstance(supplement["ci_matrix"], pd.DataFrame)
    assert len(result.result_elements) >= 2  # table + heatmap + pairwise plots
    assert result.get_html()


# --------------------------------------------------------------------------------------------------
# Ordinal handling on the Pearson path: numeric faces -> warning; non-numeric faces -> cast error
# --------------------------------------------------------------------------------------------------
def test_pearson_on_ordinal_warns_but_computes(monkeypatch):
    data = _data(_likert_frame()[["v1", "v2", "v3"]].copy())
    for name in ("v1", "v2"):
        column = data[name]
        column.column_type = ColumnType.ORDINAL
        column.is_numeric = False
        column.order = {}  # inferred from the numeric face values

    result = _run(monkeypatch, data, ["v1", "v2", "v3"], correlation_type="Pearson")

    assert result.error_message == ""
    assert result.warnings  # "ordinal columns were treated as numeric"
    assert _supplement(result)["columns"] == ["v1", "v2", "v3"]


def test_pearson_on_non_numeric_ordinal_errors(monkeypatch):
    frame = pd.DataFrame(
        {
            "v1": ["low", "mid", "high", "mid", "low", "high", "mid", "low"],
            "v2": [1, 2, 3, 2, 1, 3, 2, 1],
        }
    )
    data = Data.initialize_from_dataframe(frame)
    data["v1"].column_type = ColumnType.ORDINAL
    data["v1"].is_numeric = False
    data["v1"].order = {"low": 1, "mid": 2, "high": 3}

    result = _run(monkeypatch, data, ["v1", "v2"], correlation_type="Pearson")

    assert Style.Color.Danger.value in result.get_html()  # OrdinalCastError is rendered
    assert result.numeric_supplements() == []


# --------------------------------------------------------------------------------------------------
# The supplement is transient: the GUI recompute wrapper drops it
# --------------------------------------------------------------------------------------------------
def test_drop_numeric_supplement_clears_it(monkeypatch):
    data = _data(_likert_frame())
    result = _run(monkeypatch, data, ["v1", "v2", "v3"], correlation_type="Pearson")
    assert result.numeric_supplements()
    result.drop_numeric_supplement()
    assert result.numeric_supplements() == []
