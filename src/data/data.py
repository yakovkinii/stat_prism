#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import logging
from typing import Dict, List, Union

import numpy as np
import pandas as pd

from src.common.constant import ColumnType
from src.common.decorators import log_method
from src.pyside_ext.elements.filter import FilterSettings

ORDER_COLUMN = "__ORDER__"


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
                dataframe[column] = dataframe[column].astype(str)
            elif pd.api.types.is_float_dtype(dataframe[column]):
                dataframe[column] = dataframe[column].astype(float)
            elif pd.api.types.is_integer_dtype(dataframe[column]):
                dataframe[column] = dataframe[column].astype(int)
            else:
                logging.warning(f"Unknown type detected for {column}")
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

    def add_column_after(self,column_name:str, column:DataColumn):
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
        """Insert a column after the specified index position"""
        self.columns.insert(after_index + 1, column)
        self.update_lookups()

    def find_last_column_index(self, column_names: List[str]) -> int:
        """Find the index of the last occurrence of any column in the given list"""
        last_index = -1
        for col_name in column_names:
            if col_name in self.name_to_index:
                index = self.name_to_index[col_name]
                if index > last_index:
                    last_index = index
        return last_index

    def copy(self):
        return Data([col.copy() for col in self.columns])

    def get_dataframe(self, filters: List[FilterSettings] = None, columns: List[str] = None, map_ordinal: bool = False):
        df = pd.DataFrame({col.column_name: col.data_series for col in self.columns})
        if filters is not None and len(filters) > 0:
            for filter_settings in filters:
                query = filter_settings.get_query()
                logging.debug(f"Applying Filter: {query}")
                df = df.query(query)
        else:
            logging.debug("No filter applied")

        if columns is not None:
            missing = [col for col in columns if col not in df.columns]
            if missing:
                raise ValueError(
                    "Selected column(s) not available in the current data source: " + ", ".join(map(str, missing))
                )
            df = df[columns]

        # sort using order dicts
        for col in df.columns:
            column = self[col]
            if len(column.order) > 0:
                if map_ordinal and column.column_type == ColumnType.ORDINAL:
                    df[col] = df[col].map(column.order)
                    df = df.sort_values(col)
                else:
                    df[ORDER_COLUMN] = df[col].map(column.order)
                    df = df.sort_values(ORDER_COLUMN)
                    df = df.drop(ORDER_COLUMN, axis=1)

        return df

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


# #  Copyright (c) 2023 StatPrism Team. All rights reserved.
#
#
# import logging
# from typing import TYPE_CHECKING, Dict, List, Union
#
# import pandas as pd
# import qtawesome as qta
# from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
# from PySide6.QtGui import QColor
#
# from src._data_panel.const import DataPanelState
# from src.data.data import Data, DataColumn
# from src.common.constant import COLORS, COLUMN_TYPE_ICONS, ColumnType
# from src.common.decorators import log_method, log_method_noarg
# from src.side_area_panel.modules.common.result.registry import RESULTS
#
# if TYPE_CHECKING:
#     from src.ui_main import MainWindowClass
#
#
# class DataModel(QAbstractTableModel):
#     def __init__(self, root_class):
#         super().__init__()
#         self.root_class: MainWindowClass = root_class
#         self.state = DataPanelState.DEFAULT
#         self._data: Union[Data, None] = None
#         self.filtered_rows = []
#         self.hide_headers_mode = False
#
#     def hideHeaders(self):
#         self.hide_headers_mode = True
#
#     def unhideHeaders(self):
#         self.hide_headers_mode = False
#
#     @log_method
#     def check_and_update_column_type_and_dtype(self, column_index: int):
#         self._data[column_index].check_and_update_column_dtype()
#         self._data[column_index].automatically_update_order()
#
#     @log_method
#     def set_column_type(self, column_index: int, column_type: ColumnType):
#         self._data[column_index].column_type = column_type
#         self.check_and_update_column_type_and_dtype(column_index)
#         self.headerDataChanged.emit(Qt.Orientation.Horizontal, column_index, column_index)
#
#     @log_method
#     def load_data(self, dataframe: pd.DataFrame):
#         self.beginResetModel()
#         self._data = Data.initialize_from_dataframe(dataframe)
#         self.endResetModel()
#
#     def rowCount(self, parent=None):
#         return len(self._data[0].data_series) if self._data is not None else 0
#
#     def columnCount(self, parent=None):
#         return len(self._data.columns) if self._data is not None else 0
#
#     @log_method
#     def set_state(self, state: DataPanelState):
#         self.state = state
#         self.data_changed()
#
#     def data(self, index, role=Qt.ItemDataRole.DisplayRole):
#         if index.isValid():
#             if role in [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole]:
#                 if pd.isna(self._data[index.column()][index.row()]):
#                     return ""
#                 if self._data[index.column()][index.row()] in [None, "nan"]:
#                     return ""
#                 if (role == Qt.ItemDataRole.DisplayRole) and (
#                     self._data[index.column()].column_type == ColumnType.ORDINAL
#                 ):
#                     order = self._data[index.column()].order[self._data[index.column()][index.row()]]
#                     return f"[{order}] {self._data[index.column()][index.row()]}"
#                 return str(self._data[index.column()][index.row()])
#
#             elif role == Qt.ItemDataRole.ForegroundRole:
#                 if self.state == DataPanelState.FILTER:
#                     if index.row() in self.filtered_rows:
#                         return QColor("#f66")
#         return None
#
#     def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
#         if role == Qt.ItemDataRole.DisplayRole:
#             if orientation == Qt.Orientation.Horizontal:
#                 if self.hide_headers_mode:
#                     return None
#                 else:
#                     return str(self._data[section].column_name)
#             if orientation == Qt.Orientation.Vertical:
#                 return str(section)
#         elif role == Qt.ItemDataRole.DecorationRole and orientation == Qt.Orientation.Horizontal:
#             icons = [COLUMN_TYPE_ICONS[self._data[section].column_type]]
#             if self._data[section].inverted:
#                 icons.append(qta.icon("ri.arrow-up-down-line"))
#             return icons
#         return None
#
#     def flags(self, index):
#         return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable
#
#     @log_method
#     def setRowCount(self, count):
#         raise NotImplementedError
#
#     @log_method
#     def setColumnCount(self, count):
#         raise NotImplementedError
#
#     @log_method
#     def setHorizontalHeaderLabels(self, labels):
#         assert len(labels) == len(self._data.columns)
#         assert len(set(labels)) == len(labels)
#         self.beginResetModel()
#         for i, label in enumerate(labels):
#             self._data[i].column_name = label
#         self.endResetModel()
#
#     @log_method
#     def setItem(self, row, col, value):
#         logging.warning("setItem called")
#         self._data[col][row] = value
#         self.dataChanged.emit(self.index(row, col), self.index(row, col))
#
#     @log_method
#     def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
#         if role == Qt.ItemDataRole.EditRole:
#             self._data[index.column()][index.row()] = value
#             self.dataChanged.emit(index, index)
#             self.check_and_update_column_type_and_dtype(index.column())
#             return True
#         return False
#
#     @log_method
#     def rename_column(self, column_index: int, new_name: str):
#         if new_name in self._data.column_names():
#             logging.error("Column name already exists")
#             return
#         old_name = self._data[column_index].column_name
#
#         self.setHorizontalHeaderLabels(
#             [new_name if i == column_index else self._data.column_names()[i] for i in range(self.columnCount())]
#         )
#         # todo why is _data not modified here?
#
#         for result in RESULTS.values():
#             result.rename_column(old_name, new_name)
#
#         self.root_class.result_selector_panel.refresh()
#
#     def get_column_name(self, column_index: int):
#         if column_index is None:
#             logging.error("column_index is None")
#         assert 0 <= column_index < self.columnCount()
#         return self._data[column_index].column_name
#
#     def get_column_names(self) -> List[str]:
#         return self._data.column_names()
#
#     def get_column_ordinal_order(self, column_index: int) -> Dict[Union[int, float, str], int]:
#         return self._data[column_index].order
#
#     def get_column_ordinal_order_from_column_name(self, column_name: str) -> Dict[Union[int, float, str], int]:
#         index = self._data.name_to_index[column_name]
#         return self._data[index].order
#
#     def set_column_ordinal_order(self, column_index: int, order: Dict[Union[int, float, str], int]):
#         assert set(order.keys()) == set(self.get_column(column_index).unique())
#         self.beginResetModel()
#         self._data[column_index].order = order
#         for result in RESULTS.values():  # todo make explicit update
#             result.rename_column(self._data[column_index].column_name, self._data[column_index].column_name)
#         self.endResetModel()
#         self.root_class.result_selector_panel.refresh()
#
#     def get_all_columns_as_column_types(self):
#         return self._data.columns  # todo deprecate and maybe copy()
#
#     @log_method
#     def get_column(self, column_index: int):  # Todo deprecate and use rich classes instead
#         assert 0 <= column_index < self.columnCount()
#         return self._data[column_index].data_series
#
#     @log_method
#     def get_column_v2(self, column_index: int) -> DataColumn:
#         return self._data[column_index].copy()
#
#     @log_method
#     def get_columns(self, column_names: List[str]):
#         column_indexes = [self._data.name_to_index[name] for name in column_names]
#         return pd.concat([self._data[index] for index in column_indexes], axis=1)
#
#     @log_method
#     def set_column(self, column_index: int, values: Union[List, pd.Series]):
#         assert len(values) == self.rowCount()
#         self._data[column_index].data_series = pd.Series(values)
#         self.check_and_update_column_type_and_dtype(column_index)
#         self.dataChanged.emit(self.index(0, column_index), self.index(self.rowCount() - 1, column_index))
#
#     @log_method_noarg
#     def data_changed(self, role=Qt.ItemDataRole.DisplayRole):
#         self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount() - 1, self.columnCount() - 1), role)
#
#     @log_method_noarg
#     def get_data(self):  # Todo deprecate and use rich classes instead
#         return self._data.get_dataframe() if self._data is not None else pd.DataFrame()
#
#     @log_method_noarg
#     def get_data_v2(self) -> Data:
#         return self._data.copy()
#
#     @log_method
#     def get_column_type(self, column_index: int):
#         return self._data[column_index].column_type
#
#     @log_method
#     def get_column_type_from_column_name(self, column_name: str):
#         index = self._data.name_to_index[column_name]
#         return self._data[index].column_type
#
#     @log_method
#     def add_column(self, column_to_the_left_index):
#         self.beginInsertColumns(QModelIndex(), column_to_the_left_index + 1, column_to_the_left_index + 1)
#         self._data.add_new_column(column_to_the_left_index)
#         self.endInsertColumns()
#
#     @log_method
#     def delete_column(self, column_index):
#         self.beginRemoveColumns(QModelIndex(), column_index, column_index)
#         self._data.columns = self._data.columns[:column_index] + self._data.columns[column_index + 1 :]
#         self._data.update_lookups()
#         self.endRemoveColumns()
#
#     @log_method
#     def delete_columns(self, column_indexes):
#         self.beginRemoveColumns(QModelIndex(), min(column_indexes), max(column_indexes))
#         for index in column_indexes:
#             self.delete_column(index)
#         self.endRemoveColumns()
#
#     def get_column_color(self, column_index):
#         return self._data[column_index].color
#
#     @log_method
#     def set_column_color(self, column_index, color):
#         self._data[column_index].color = color
#         self.headerDataChanged.emit(Qt.Orientation.Horizontal, column_index, column_index)
#
#     @log_method
#     def toggle_column_inverted(self, column_index):
#         self._data[column_index].inverted = not self._data[column_index].inverted
#         self.headerDataChanged.emit(Qt.Orientation.Horizontal, column_index, column_index)
#
#     @log_method
#     def save_as_xlsx(self, filename):
#         def apply_style(column):
#             color = self._data[column].color
#             if color is not None:
#                 return f"background-color: {COLORS[color]};"
#             return "background-color: #eee;"
#
#         try:
#             self.get_data().style.applymap_index(apply_style, axis=1)
#             .to_excel(filename, engine="openpyxl", index=False)
#         except Exception as e:
#             logging.error(e)
#         logging.info(f"Saved to {filename}")
