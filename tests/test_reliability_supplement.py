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

"""Headless coverage of the Reliability module via its numeric supplements.

Reliability attaches a numeric supplement to each result table: the coefficients table carries
the scale-level numbers (alpha / omega), the if-item-removed table the per-item stats. These tests
drive ``recalculate_reliability_study`` headlessly (offscreen QApplication from conftest,
DATA_MANAGER monkeypatched), fetch the supplements, and assert they carry exactly what
``compute_reliability`` produces -- across coefficient, omega, item-table and error branches.
"""

import math

import numpy as np
import pandas as pd
import pytest

from src.common.constant import ColumnType
from src.data.data import Data
from src.pyside_ext.styling import Style
from src.side_area_panel.modules.reliability import reliability_main
from src.side_area_panel.modules.reliability.reliability_main import compute_reliability, recalculate_reliability_study
from src.side_area_panel.modules.reliability.reliability_result import (
    ReliabilityResult,
    ReliabilityStudyConfig,
)
from src.side_area_panel.modules.correlation.correlation_result import CORRELATION_TYPE_MAP, CorrelationType

LIKERT_KEYS = ["Pearson", "Spearman", "Kendall", "Kendall tau c", "Polychoric"]
BINARY_KEYS = ["Phi", "Tetrachoric"]


# --------------------------------------------------------------------------------------------------
# Test data
# --------------------------------------------------------------------------------------------------
def _likert_frame() -> pd.DataFrame:
    rng = np.random.default_rng(2024)
    n = 80
    latent = rng.normal(size=n)

    def likert(load):
        x = load * latent + rng.normal(scale=0.8, size=n)
        ranks = pd.Series(x).rank(method="first").to_numpy()
        return (((ranks - 1) * 5 // n) + 1).astype(int)  # 1..5, every category present

    return pd.DataFrame({"i1": likert(1.0), "i2": likert(0.9), "i3": likert(0.8), "i4": likert(0.7)})


def _binary_frame() -> pd.DataFrame:
    rng = np.random.default_rng(99)
    n = 80
    latent = rng.normal(size=n)

    def binary(load):
        x = load * latent + rng.normal(scale=0.8, size=n)
        return (x > np.median(x)).astype(int)

    return pd.DataFrame({"i1": binary(1.0), "i2": binary(0.9), "i3": binary(0.8), "i4": binary(0.7)})


def _data(frame: pd.DataFrame) -> Data:
    return Data.initialize_from_dataframe(frame)


def _data_for(type_key: str):
    frame = _binary_frame() if type_key in BINARY_KEYS else _likert_frame()
    return _data(frame), ["i1", "i2", "i3", "i4"]


# --------------------------------------------------------------------------------------------------
# Driving the module headlessly
# --------------------------------------------------------------------------------------------------
def _run(monkeypatch, data, items, **cfg_kwargs) -> ReliabilityResult:
    monkeypatch.setattr(reliability_main.DATA_MANAGER, "get_data_from_data_label", lambda *a, **k: data)
    cfg = ReliabilityStudyConfig(
        data_source="Auto",
        column_selector=[list(items)],
        **cfg_kwargs,
    )
    result = ReliabilityResult(unique_id=1, settings_panel_index=0, config=cfg)
    return recalculate_reliability_study(None, result, lambda _p: None)


def _prepare_df(data: Data, items, kind: CorrelationType) -> pd.DataFrame:
    if kind == CorrelationType.PEARSON:
        df, _ = data.get_numeric_face_dataframe(list(items))
        return df
    return data.get_dataframe(columns=list(items), map_ordinal=True)


def _num_eq(a, b) -> bool:
    if isinstance(a, float) and math.isnan(a):
        return isinstance(b, float) and math.isnan(b)
    if isinstance(a, float) or isinstance(b, float):
        return abs(float(a) - float(b)) < 1e-9
    return a == b


# --------------------------------------------------------------------------------------------------
# Every coefficient, omega on/off: coefficients-table supplement matches compute_reliability
# --------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("type_key", LIKERT_KEYS + BINARY_KEYS)
@pytest.mark.parametrize("omega", [True, False])
def test_coef_supplement_matches_compute(monkeypatch, type_key, omega):
    kind = CORRELATION_TYPE_MAP[type_key]
    data, items = _data_for(type_key)

    result = _run(
        monkeypatch,
        data,
        items,
        correlation_type=type_key,
        mcdonald_omega=omega,
        item_deleted_table=False,
        scale_name="Scale",
    )

    assert result.error_message == ""
    supplements = result.numeric_supplements()
    assert len(supplements) == 1  # only the coefficients table (item table is off)
    coef = supplements[0]

    expected = compute_reliability(result.config, _prepare_df(data, items, kind))
    assert coef["scale_name"] == expected.scale_name
    assert coef["n_items"] == expected.n_items == len(items)
    assert _num_eq(coef["alpha"], expected.alpha)
    assert _num_eq(coef["omega"], expected.omega)
    if not omega:
        assert math.isnan(coef["omega"])
    assert result.get_html()


# --------------------------------------------------------------------------------------------------
# If-item-removed table: present only when enabled, and its supplement carries the per-item stats
# --------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("item_table", [True, False])
def test_item_table_supplement_presence_and_content(monkeypatch, item_table):
    data, items = _data_for("Spearman")
    result = _run(
        monkeypatch,
        data,
        items,
        correlation_type="Spearman",
        mcdonald_omega=True,
        item_deleted_table=item_table,
    )

    assert result.error_message == ""
    supplements = result.numeric_supplements()
    if not item_table:
        assert len(supplements) == 1  # coefficients table only
        return

    assert len(supplements) == 2  # coefficients table + item table (in element order)
    item_supplement = supplements[1]
    assert len(item_supplement["items"]) == len(items)

    expected = compute_reliability(result.config, _prepare_df(data, items, CorrelationType.SPEARMAN))
    for actual_item, expected_item in zip(item_supplement["items"], expected.items):
        assert actual_item.name == expected_item.name
        assert _num_eq(actual_item.item_rest, expected_item.item_rest)
        assert _num_eq(actual_item.alpha_deleted, expected_item.alpha_deleted)
        assert _num_eq(actual_item.omega_deleted, expected_item.omega_deleted)


# --------------------------------------------------------------------------------------------------
# Verbal indicators + numbering + prose all on at once
# --------------------------------------------------------------------------------------------------
def test_extras_branches_render(monkeypatch):
    data, items = _data_for("Pearson")
    result = _run(
        monkeypatch,
        data,
        items,
        correlation_type="Pearson",
        mcdonald_omega=True,
        item_deleted_table=True,
        verbal_indicators=True,
        number_columns=True,
        interpretation="Full",
    )
    assert result.error_message == ""
    assert len(result.numeric_supplements()) == 2
    assert result.get_html()


# --------------------------------------------------------------------------------------------------
# Error branches: too few items, and a binary estimator on non-binary data
# --------------------------------------------------------------------------------------------------
def test_too_few_items_errors(monkeypatch):
    data, _items = _data_for("Pearson")
    result = _run(monkeypatch, data, ["i1"], correlation_type="Pearson")
    assert Style.Color.Danger.value in result.get_html()  # reliability.error.min_items is rendered
    assert result.numeric_supplements() == []


@pytest.mark.parametrize("type_key", BINARY_KEYS)
def test_binary_estimator_on_non_binary_errors(monkeypatch, type_key):
    data = _data(_likert_frame())  # 1..5, not dichotomous
    result = _run(monkeypatch, data, ["i1", "i2", "i3", "i4"], correlation_type=type_key)
    assert Style.Color.Danger.value in result.get_html()  # reliability.msg.binary_required is rendered
    assert result.numeric_supplements() == []


# --------------------------------------------------------------------------------------------------
# Ordinal handling on the Pearson path: numeric faces -> warning; non-numeric faces -> cast error
# --------------------------------------------------------------------------------------------------
def test_pearson_on_ordinal_warns_but_computes(monkeypatch):
    data = _data(_likert_frame())
    for name in ("i1", "i2"):
        column = data[name]
        column.column_type = ColumnType.ORDINAL
        column.is_numeric = False
        column.order = {}  # inferred from the numeric face values

    result = _run(monkeypatch, data, ["i1", "i2", "i3", "i4"], correlation_type="Pearson")

    assert result.error_message == ""
    assert result.warnings  # "ordinal columns were treated as numeric"
    assert result.numeric_supplements()[0]["n_items"] == 4


def test_pearson_on_non_numeric_ordinal_errors(monkeypatch):
    frame = pd.DataFrame(
        {
            "i1": ["low", "mid", "high", "mid", "low", "high", "mid", "low"],
            "i2": [1, 2, 3, 2, 1, 3, 2, 1],
        }
    )
    data = Data.initialize_from_dataframe(frame)
    data["i1"].column_type = ColumnType.ORDINAL
    data["i1"].is_numeric = False
    data["i1"].order = {"low": 1, "mid": 2, "high": 3}

    result = _run(monkeypatch, data, ["i1", "i2"], correlation_type="Pearson")

    assert Style.Color.Danger.value in result.get_html()  # OrdinalCastError is rendered
    assert result.numeric_supplements() == []


# --------------------------------------------------------------------------------------------------
# Supplements are transient: the GUI recompute wrapper drops them
# --------------------------------------------------------------------------------------------------
def test_drop_numeric_supplement_clears_them(monkeypatch):
    data, items = _data_for("Pearson")
    result = _run(monkeypatch, data, items, correlation_type="Pearson", item_deleted_table=True)
    assert result.numeric_supplements()
    result.drop_numeric_supplement()
    assert result.numeric_supplements() == []
