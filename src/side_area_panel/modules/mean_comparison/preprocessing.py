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


from __future__ import annotations

import pandas as pd
from typing import TYPE_CHECKING

from src.common.constant import ColumnType, MDASH
from src.data.data import Data, category_display_series, is_empty_value, sorted_numeric_or_alpha
from src.side_area_panel.modules.common.utility import format_value_apa
from src.side_area_panel.modules.mean_comparison.constant import MeanComparisonMethod, MissingValuesInGrouping

if TYPE_CHECKING:
    from src.side_area_panel.modules.mean_comparison.mean_comparison_result import MeanComparisonStudyConfig


def prepare_df_for_mean_comparison(
    data: Data,
    cfg: MeanComparisonStudyConfig,
    map_ordinal: bool = False,
) -> pd.DataFrame:
    """
    Returns a dataframe with selected value columns + grouping column and filters applied,
    and handles missing values in the grouping column according to cfg.grouping_missing.

    Note: Value columns are left as-is here; downstream tests should dropna explicitly.
    """
    selected_columns = cfg.column_selector[0]

    grouping_column = cfg.column_selector[1][0]
    df = data.get_dataframe(
        columns=selected_columns + [grouping_column],
        map_ordinal=map_ordinal,
    ).copy()

    # The grouping column only splits rows into groups; it must never be mapped to internal order
    # codes (only the value columns are, for the nonparametric tests). Restore its face values so
    # group names and ordering are always the visible categories, and the mapped/unmapped frames
    # agree on which rows each group holds.
    if map_ordinal and data[grouping_column].column_type == ColumnType.ORDINAL:
        df[grouping_column] = data[grouping_column].data_series

    if cfg.grouping_missing == MissingValuesInGrouping.SKIP.value:
        df = df[~df[grouping_column].apply(is_empty_value)].copy()
    elif cfg.grouping_missing == MissingValuesInGrouping.TREAT_AS_NA.value:
        # Standardize missing-like values to the same display label used elsewhere.
        df[grouping_column] = category_display_series(df[grouping_column])
    else:
        raise ValueError(f"Unknown MissingValuesInGrouping option: {cfg.grouping_missing}")

    # Group labels are only ever used as text (table headers, plot legends, prose). Normalize once
    # so all downstream comparisons are string-only and NaN-safe.
    df[grouping_column] = category_display_series(df[grouping_column])

    # Order the rows by the grouping column's display order (prescribed order first, else
    # alphabetical) once, here: every downstream table/plot then lists groups the same way via a
    # plain unique()/groupby, with no need to reorder (or thread the column order) per processor.
    rank_of = {group: index for index, group in enumerate(ordered_groups(data, grouping_column, df))}
    df = df.sort_values(by=grouping_column, key=lambda s: s.map(rank_of), kind="stable")

    return df


def split_value_columns(data: Data, cfg: MeanComparisonStudyConfig, df: pd.DataFrame):
    """Split the selected value columns for the ordinal-treatment rule, mutating ``df`` when needed.

    The parametric family does not support ordinals, so an explicit parametric method
    (homogeneous / inhomogeneous) casts ordinal columns to their numeric face values in ``df`` and
    tests them parametrically; AUTO and the non-parametric method keep ordinals in the rank-based
    (fully-ordinal) path. Nominal columns always stay in the rank-based path.

    Returns ``(numeric_columns, non_numeric_columns, cast_ordinals)`` -- ``cast_ordinals`` lists the
    ordinal columns cast to numeric, so the caller can warn. Raises :class:`OrdinalCastError` when an
    explicit parametric method is asked to use an ordinal whose face values are not all numeric."""
    selected_columns = cfg.column_selector[0]
    parametric_method = cfg.method in (
        MeanComparisonMethod.HOMOGENEOUS.value,
        MeanComparisonMethod.INHOMOGENEOUS.value,
    )
    cast_ordinals = []
    if parametric_method:
        cast_ordinals = [c for c in selected_columns if data[c].column_type == ColumnType.ORDINAL]
        # Validate the face values are numeric (raises OrdinalCastError otherwise), then cast them in
        # the shared frame so the parametric processors see numbers rather than category labels.
        data.get_numeric_face_dataframe(cast_ordinals)
        for col in cast_ordinals:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        numeric_columns = [
            c for c in selected_columns if data[c].column_type in (ColumnType.NUMERIC, ColumnType.ORDINAL)
        ]
    else:
        numeric_columns = [c for c in selected_columns if data[c].column_type == ColumnType.NUMERIC]
    non_numeric_columns = [c for c in selected_columns if c not in numeric_columns]
    return numeric_columns, non_numeric_columns, cast_ordinals


def ordered_groups(data: Data, grouping_column: str, df: pd.DataFrame) -> list:
    """Distinct group values present in ``df``, in display order: the grouping column's prescribed
    order first, then anything else alphabetically. The prepared frame stores normalized display
    labels, so order is applied by mapping raw values to the same labels before comparison."""
    present = list(df[grouping_column].dropna().unique())
    ordered = data.ordered_category_labels(grouping_column, list(data[grouping_column].data_series.unique()))
    ranked = [label for label in ordered if label in set(present)]
    rest = sorted_numeric_or_alpha(g for g in present if g not in set(ranked))
    return ranked + rest


def _face_label(value):
    return value if isinstance(value, str) else format_value_apa(value)


def _ordinal_iqr(q1, q3):
    # IQR = Q3 - Q1, but only when the face-value quartiles are numeric; ordinal categories permit no
    # subtraction, so non-numeric labels give a dash.
    try:
        return format_value_apa(float(q3) - float(q1))
    except (TypeError, ValueError):
        return MDASH


def median_iqr_display(data: Data, column_name: str, series: pd.Series):
    """Median + IQR display cells for a (possibly ordinal) column.

    Nonparametric tests use ordinal order codes internally; these cells must never expose those
    codes. For an ordinal column the median (and quartiles) are mapped back to the user-facing
    category, and the IQR is the numeric spread of the face-value quartiles when those are numeric,
    otherwise a dash.
    """
    clean = series.dropna()
    if clean.empty:
        return MDASH, MDASH
    if data[column_name].column_type != ColumnType.ORDINAL:
        return (
            format_value_apa(clean.median()),
            format_value_apa(clean.quantile(0.75) - clean.quantile(0.25)),
        )

    # Non-interpolating quantiles so each is a real category (never an averaged code), shown as its
    # face label.
    median = data.to_face_value(column_name, clean.quantile(0.5, interpolation="nearest"))
    q1 = data.to_face_value(column_name, clean.quantile(0.25, interpolation="nearest"))
    q3 = data.to_face_value(column_name, clean.quantile(0.75, interpolation="nearest"))
    return _face_label(median), _ordinal_iqr(q1, q3)
