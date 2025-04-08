#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#
import logging
from typing import Callable, Dict, List, Union

import numpy as np
import pandas as pd

from src.common.constant import ColumnType
from src.common.elements.filter.filter import FilterSettings


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
        color: int,
        order: Dict[Union[int, float, str], int],
    ):
        self.column_name: str = column_name
        self.original_name: str = original_name
        self.data_series: pd.Series = data_series
        self.column_dtype: str = column_dtype
        self.column_type: ColumnType = column_type
        self.is_numeric: bool = is_numeric
        self.inverted: bool = inverted
        self.color: int = color
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
            data_series = data_series.astype(str)
            dtype = "str"

        return cls(
            column_name=str(data_series.name),
            original_name=str(data_series.name),
            data_series=data_series,
            column_dtype=dtype,
            column_type=ColumnType.NUMERIC if dtype in ["int", "float"] else ColumnType.NOMINAL,
            is_numeric=dtype in ["int", "float"],
            inverted=False,
            color=0,
            order={},
        ).automatically_update_order()

    def automatically_update_order(self):
        if self.column_type not in [ColumnType.ORDINAL, ColumnType.NOMINAL]:
            self.order = {}
            return self

        self.order = {o: i for i, o in enumerate(sorted(self.order, key=self.order.get))}
        unique_values = self.data_series.sort_values().unique()
        for value in sorted(unique_values):
            if value not in self.order:
                order = max(self.order.values()) + 1 if len(self.order) > 0 else 1
                logging.warning(f"Value {value} added to ordinal_order with order {order}")
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
                    self.data_series = self.data_series.astype(str)
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


class Data:
    def __init__(self, columns: List[DataColumn]):
        self.columns: List[DataColumn] = columns
        self.name_to_index: Dict[str, int] = {}
        self.update_lookups()

    @classmethod
    def initialize_from_dataframe(cls, dataframe: pd.DataFrame):
        for column in dataframe.columns:
            if pd.api.types.is_string_dtype(dataframe[column]):
                dataframe[column] = dataframe[column].astype(str)
            elif pd.api.types.is_float_dtype(dataframe[column]):
                dataframe[column] = dataframe[column].astype(float)
            elif pd.api.types.is_integer_dtype(dataframe[column]):
                dataframe[column] = dataframe[column].astype(int)
            else:
                logging.error(f"Unknown type detected for {column}")
                logging.info("Trying to convert to string")
                dataframe[column] = dataframe[column].astype(str)

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

    def __getitem__(self, item)->DataColumn:
        if isinstance(item, str):
            return self.columns[self.name_to_index[item]]
        return self.columns[item]

    def column_names(self):
        return [col.column_name for col in self.columns]

    def add_new_column(self, column_to_the_left_index):
        suffix = 1
        while f"New column {suffix}" in self.column_names():
            suffix += 1
        new_column_name = f"New column {suffix}"

        new_column = DataColumn.initialize_from_series(
            pd.Series([""] * len(self.columns[0].data_series), name=new_column_name)
        )
        self.columns.insert(column_to_the_left_index + 1, new_column)
        self.update_lookups()
        return new_column

    def copy(self):
        return Data([col.copy() for col in self.columns])

    def get_dataframe(self, filters: List[FilterSettings]=None, columns: List[str]=None):
        df = pd.DataFrame({col.column_name: col.data_series for col in self.columns})
        if filters is not None and len(filters) > 0:
            for filter_settings in filters:
                query = filter_settings.get_query()
                logging.debug(f"Applying Filter: {query}")
                df = df.query(query)
        else:
            logging.debug("No filter applied")

        if columns is not None:
            df = df[columns]
        return df
