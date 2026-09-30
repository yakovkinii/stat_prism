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


import logging
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd

from src.common.constant import ID_COLUMN_NAME, ColumnType
from src.common.decorators import log_method

ORDER_COLUMN = "__ORDER__"


def sorted_numeric_or_alpha(values):
    """Default category sort: numeric when every value is castable to a number, else alphabetical.
    So Likert-style labels ('1'..'10') sort 1, 2, ..., 10 rather than '1', '10', '2', while text
    categories fall back to alphabetical."""
    items = list(values)
    try:
        return sorted(items, key=lambda v: float(v))
    except (TypeError, ValueError):
        return sorted(items, key=str)


def infer_ordinal_order(column) -> dict:
    """The column's ordinal order as ``{face_value: code}``.

    An ordinal column carries an ``order`` dict only when the user has prescribed one; when it is
    absent the order is inferred on demand by the standard rule -- numeric when every value casts to a
    number, else alphabetical. This way a study always has a mapping to work with, without an order
    being eagerly stored on every ordinal column. Operates on a column object so both a :class:`Data`
    instance and UI editors (which hold column objects, not a Data) can share it."""
    if column.order:
        return column.order
    values = [v for v in column.data_series.dropna().unique() if not (isinstance(v, str) and v == "")]
    return {value: index for index, value in enumerate(sorted_numeric_or_alpha(values), start=1)}


class OrdinalCastError(Exception):
    """An ordinal column whose face values are not all numeric was fed to a module that must treat it
    numerically. Carries the column name so the module can show a clear 'convert first' message."""

    def __init__(self, column_name: str):
        self.column_name = column_name
        super().__init__(column_name)


class DataColumn:
    def __init__(
        self,
        column_name: str,
        original_name: str,
        data_series: pd.Series,
        column_dtype: str,
        column_type: ColumnType,
        is_numeric: bool,
        inverted: bool,
        color: Optional[str],
        order: Dict[Union[int, float, str], int],
    ):
        self.column_name: str = column_name
        self.original_name: str = original_name
        self.data_series: pd.Series = data_series
        self.column_dtype: str = column_dtype
        self.column_type: ColumnType = column_type
        self.is_numeric: bool = is_numeric
        self.inverted: bool = inverted
        # Hex color code or None for no color.
        self.color: Optional[str] = color
        self.order: Dict[Union[int, float, str], int] = order

    @classmethod
    def initialize_from_series(cls, data_series: pd.Series):
        dtype = None
        if pd.api.types.is_integer_dtype(data_series):
            dtype = "int"
        if pd.api.types.is_float_dtype(data_series):
            dtype = "float"
        if pd.api.types.is_string_dtype(data_series):
            dtype = "str"

        if dtype is None:
            logging.warning(f"Unknown type detected for {data_series.name}. Trying to convert to string")
            data_series = data_series.fillna("").astype(str)
            dtype = "str"

        if dtype == "str":
            data_series = data_series.fillna("").astype(str)

        return cls(
            column_name=str(data_series.name),
            original_name=str(data_series.name),
            data_series=data_series,
            column_dtype=dtype,
            column_type=ColumnType.NUMERIC if dtype in ["int", "float"] else ColumnType.NOMINAL,
            is_numeric=dtype in ["int", "float"],
            inverted=False,
            color=None,
            order={},
        ).automatically_update_order()

    def automatically_update_order(self):
        if self.column_type not in [ColumnType.ORDINAL, ColumnType.NOMINAL]:
            self.order = {}
            return self

        # Ordinal / nominal columns carry an order dict only when one has been prescribed. With none
        # set, leave it empty -- ordinal studies infer the order on demand (see infer_ordinal_order).
        # When a (partial) order is present, re-index it and append any values still lacking a place.
        if not self.order:
            return self

        self.order = {o: i for i, o in enumerate(sorted(self.order, key=self.order.get), start=1)}
        unique_values = self.data_series.dropna().unique()
        for value in sorted_numeric_or_alpha(unique_values):
            if isinstance(value, str) and value == "":
                continue
            if value not in self.order:
                order = max(self.order.values()) + 1 if len(self.order) > 0 else 1
                self.order[value] = order
        return self

    def check_and_update_column_dtype(self):
        # try casting to int. if fail - cast to float. if fail - cast to str
        try:
            self.data_series = self.data_series.astype(int)
            self.column_dtype = "int"
        except ValueError:
            try:
                self.data_series = self.data_series.replace("", np.nan).astype(float)
                self.column_dtype = "float"
            except ValueError:
                try:
                    self.data_series = self.data_series.fillna("").astype(str)
                    self.column_dtype = "str"
                    logging.warning(f"Column {self.column_name} was cast to str")
                    if self.column_type == ColumnType.NUMERIC:
                        self.column_type = ColumnType.NOMINAL
                        logging.warning(f"Column {self.column_name} was cast to NOMINAL")
                except ValueError:
                    raise ValueError(f"Could not cast column {self.column_name} to any type")

    def __getitem__(self, item):
        if isinstance(item, str):
            return self.data_series[item]
        return self.data_series.iloc[item]

    def copy(self):
        return DataColumn(
            self.column_name,
            self.original_name,
            self.data_series.copy(),
            self.column_dtype,
            self.column_type,
            self.is_numeric,
            self.inverted,
            self.color,
            self.order,
        )

    def rename(self, new_name: str):
        self.column_name = new_name
        self.data_series.rename(new_name, inplace=True)


class Data:
    def __init__(self, columns: List[DataColumn]):
        self.columns: List[DataColumn] = columns
        self.name_to_index: Dict[str, int] = {}
        self.update_lookups()

    @classmethod
    def initialize_from_dataframe(cls, dataframe: pd.DataFrame):
        for column in dataframe.columns:
            if pd.api.types.is_string_dtype(dataframe[column]):
                dataframe[column] = dataframe[column].fillna("").astype(str)
            elif pd.api.types.is_float_dtype(dataframe[column]):
                dataframe[column] = dataframe[column].astype(float)
            elif pd.api.types.is_integer_dtype(dataframe[column]):
                dataframe[column] = dataframe[column].astype(int)
            else:
                logging.warning(f"Unknown type detected for {column}")
                logging.info("Trying to convert to string")
                dataframe[column] = dataframe[column].fillna("").astype(str)

        dataframe.columns = pd.Index([str(column) for column in dataframe.columns])
        if len(set(dataframe.columns)) != len(dataframe.columns):
            logging.warning("Duplicate column names detected")
            columns = list(dataframe.columns)
            new_columns = []
            for column in columns:
                if new_columns.count(column) > 0:
                    new_columns.append(f"{column} ({new_columns.count(column)})")
                else:
                    new_columns.append(column)

            dataframe.columns = new_columns

        dataframe.columns = pd.Index([str(column) for column in dataframe.columns])

        return Data([DataColumn.initialize_from_series(dataframe[col]) for col in dataframe.columns])

    def update_lookups(self):
        self.name_to_index = {col.column_name: i for i, col in enumerate(self.columns)}

    def __getitem__(self, item) -> DataColumn:
        if isinstance(item, str):
            return self.columns[self.name_to_index[item]]
        return self.columns[item]

    def column_names(self):
        return [col.column_name for col in self.columns]

    def add_column_first(self, column: DataColumn):
        if column.column_name in self.name_to_index:
            raise ValueError(f"Column name {column.column_name} already exists.")
        self.columns.insert(0, column)
        self.update_lookups()

    def add_column_after(self, column_name: str, column: DataColumn):
        if column.column_name in self.name_to_index:
            raise ValueError(f"Column name {column.column_name} already exists.")
        column_to_the_left_index = self.name_to_index[column_name]
        self.columns.insert(column_to_the_left_index + 1, column)
        self.update_lookups()

    def replace_column(self, column_name, new_column: DataColumn):
        if column_name not in self.name_to_index:
            raise ValueError(f"Column name {column_name} does not exist.")
        index = self.name_to_index[column_name]
        self.columns[index] = new_column
        self.update_lookups()

    def remove_column(self, column_name: str):
        if column_name not in self.name_to_index:
            raise ValueError(f"Column name {column_name} does not exist.")
        del self.columns[self.name_to_index[column_name]]
        self.update_lookups()

    def rename_column(self, old_name: str, new_name: str):
        if old_name not in self.name_to_index:
            raise ValueError(f"Column name {old_name} does not exist.")
        self.columns[self.name_to_index[old_name]].rename(new_name)
        self.update_lookups()

    def insert_column_after_index(self, column: "DataColumn", after_index: int):
        self.columns.insert(after_index + 1, column)
        self.update_lookups()

    def find_last_column_index(self, column_names: List[str]) -> int:
        last_index = -1
        for col_name in column_names:
            if col_name in self.name_to_index:
                index = self.name_to_index[col_name]
                if index > last_index:
                    last_index = index
        return last_index

    def copy(self):
        return Data([col.copy() for col in self.columns])

    def get_dataframe(self, columns: List[str] = None, map_ordinal: bool = False, include_id_column: bool = False):
        if include_id_column:
            # include_id_column only makes sense alongside an explicit column list; there is
            # no use case for it with columns=None (which means "all columns").
            if columns is None:
                raise ValueError("include_id_column=True requires an explicit `columns` list")
            columns = columns + [ID_COLUMN_NAME]

        df = pd.DataFrame({col.column_name: col.data_series for col in self.columns})

        if columns is not None:
            missing = [col for col in columns if col not in df.columns]
            if missing:
                raise ValueError(
                    "Selected column(s) not available in the current data source: " + ", ".join(map(str, missing))
                )
            df = df[columns]

        # Sort by order dicts. Ordinals use their prescribed order or, when none is stored, the order
        # inferred on demand (so an ordinal always sorts / maps consistently); nominals sort only when
        # an explicit order is present.
        for col in df.columns:
            column = self[col]
            if column.column_type == ColumnType.ORDINAL:
                effective_order = infer_ordinal_order(column)
                if not effective_order:
                    continue
                if map_ordinal:
                    df[col] = df[col].map(effective_order)
                    df = df.sort_values(col)
                else:
                    df[ORDER_COLUMN] = df[col].map(effective_order)
                    df = df.sort_values(ORDER_COLUMN)
                    df = df.drop(ORDER_COLUMN, axis=1)
            elif len(column.order) > 0:
                df[ORDER_COLUMN] = df[col].map(column.order)
                df = df.sort_values(ORDER_COLUMN)
                df = df.drop(ORDER_COLUMN, axis=1)

        return df

    def get_series(self, column: str, map_ordinal: bool = False) -> pd.Series:
        return self.get_dataframe(columns=[column], map_ordinal=map_ordinal)[column]

    def to_mapped_ints(self, column_name: str) -> pd.Series:
        """Ordinal values as internal order codes for analysis calculations."""
        return self.get_series(column_name, map_ordinal=True)

    def to_face_value(self, column_name: str, code):
        """Map an ordinal analysis code back to the value shown to the user."""
        return self.ordered_value_label(column_name, code)

    def get_numeric_face_dataframe(self, columns):
        """DataFrame for modules that must treat their inputs as numeric. Numeric columns pass through;
        an ORDINAL column has its FACE values cast to numeric (never the internal order codes), and an
        ordinal whose face values are not all numeric raises :class:`OrdinalCastError`. Returns
        ``(df, cast_ordinals)`` -- ``cast_ordinals`` lists the ordinal columns that were cast, so the
        caller can show the 'treated as numeric' warning."""
        df = self.get_dataframe(columns=columns)
        cast = []
        for col in columns:
            if self[col].column_type != ColumnType.ORDINAL:
                continue
            numeric = pd.to_numeric(df[col], errors="coerce")
            non_missing = df[col].notna() & (df[col].astype(str).str.strip() != "")
            if bool((numeric.isna() & non_missing).any()):
                raise OrdinalCastError(col)
            df[col] = numeric
            cast.append(col)
        return df, cast

    def get_id_series(self) -> pd.Series:
        return self.get_dataframe(columns=[ID_COLUMN_NAME])[ID_COLUMN_NAME]

    def ordered_categories(self, column_name: str, values) -> list:
        """Order category `values` by the column's defined order (its ordinality for
        ordinal columns; the stored order for nominal), with any value missing from the
        order dict appended in natural sort. Use this for the *display* order of
        categories, because pandas `crosstab` / `value_counts().sort_index()` otherwise
        sort alphabetically and ignore the user-defined ordinal order."""
        order = self[column_name].order or {}
        present = sorted((v for v in values if v in order), key=lambda v: order[v])
        # No prescribed order -> default sort (numeric when castable, else alphabetical), for both
        # nominal and ordinal; any value missing from a partial order is appended the same way.
        missing = sorted_numeric_or_alpha(v for v in values if v not in order)
        return present + missing

    def ordered_value_label(self, column_name: str, code):
        """Map an ordinal analysis code back to the displayed category/value.

        Exact codes return their category. Interpolated medians/quartiles between two
        ordered categories are shown on the visible numeric scale when possible, otherwise
        as the adjacent displayed labels, so result tables do not expose internal order keys.
        """
        order = infer_ordinal_order(self[column_name])
        if not order or pd.isna(code):
            return code

        by_code = {float(v): k for k, v in order.items()}
        code = float(code)
        if code in by_code:
            return by_code[code]

        lower = max((k for k in by_code if k < code), default=None)
        upper = min((k for k in by_code if k > code), default=None)
        if lower is None or upper is None:
            return code

        lo, hi = by_code[lower], by_code[upper]
        try:
            lo_num, hi_num = float(lo), float(hi)
            if np.isfinite(lo_num) and np.isfinite(hi_num):
                value = lo_num + (code - lower) * (hi_num - lo_num) / (upper - lower)
                return int(value) if float(value).is_integer() else value
        except (TypeError, ValueError):
            pass
        return f"{lo}/{hi}"

    def n_columns(self):
        return len(self.columns)

    def n_rows(self):
        if len(self.columns) == 0:
            return 0
        return len(self.columns[0].data_series)

    def get_all_columns_as_column_types(self):
        return self.columns  # todo deprecate and maybe copy()

    @log_method
    def get_column_type_from_column_name(self, column_name: str):
        index = self.name_to_index[column_name]
        return self[index].column_type
