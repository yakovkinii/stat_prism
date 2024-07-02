import logging
from typing import Union, List, Dict

import numpy as np
import qtawesome as qta
import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex
from PyQt5.QtGui import QColor

from core.panels.data_panel.data.flags import ColumnFlags, ColumnFlagsRegistry
from core.registry.utility import log_method, log_method_noarg


class DataModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Current loaded dataframe
        self._df_all: pd.DataFrame = pd.DataFrame()
        # Current displayed dataframe
        self._df: pd.DataFrame = pd.DataFrame()

        self.column_flags: Dict[str, ColumnFlags] = {}
        self.hide_headers_mode = False
        self.load_data(pd.read_csv("data.csv"))

    def hideHeaders(self):
        self.hide_headers_mode = True

    def unhideHeaders(self):
        self.hide_headers_mode = False

    @log_method
    def load_data(self, dataframe: pd.DataFrame):
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

        dataframe.columns = [str(column) for column in dataframe.columns]
        self.beginResetModel()
        self._df_all = dataframe.copy()
        self._df = dataframe.copy()
        self.column_flags = {}
        for column in dataframe.columns:
            self.column_flags[column] = ColumnFlags(dataframe[column])
        self.endResetModel()

    def rowCount(self, parent=None):
        return self._df.shape[0]

    def columnCount(self, parent=None):
        return self._df.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._df.iloc[index.row(), index.column()])
            # elif role == Qt.BackgroundRole:
            #     return QColor(0, 0, 255)
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if self.hide_headers_mode == True:
                    return None
                else:
                    return str(self._df.columns[section])

            if orientation == Qt.Vertical:
                return str(section)
        elif role == Qt.DecorationRole and orientation == Qt.Horizontal:
            column_name = self._df.columns[section]
            icons = []
            if self.column_flags[column_name].get_flag(ColumnFlagsRegistry.inverted):
                icons.append(qta.icon("ri.arrow-up-down-line"))

            return icons
        return None

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    @log_method
    def setRowCount(self, count):
        logging.error("setRowCount called")
        raise NotImplementedError

    @log_method
    def setColumnCount(self, count):
        logging.warning("setColumnCount called")
        raise NotImplementedError

    @log_method
    def setHorizontalHeaderLabels(self, labels):
        assert len(labels) == self._df.shape[1]
        assert len(set(labels)) == len(labels)
        self.beginResetModel()
        old_labels = self._df.columns
        self._df = self._df.rename(columns=dict(zip(old_labels, labels)))
        self._df_all = self._df_all.rename(columns=dict(zip(old_labels, labels)))
        for i, column in enumerate(old_labels):
            self.column_flags[labels[i]] = self.column_flags.pop(column)
        self.endResetModel()

    @log_method
    def setItem(self, row, col, value):
        logging.warning("setItem called")
        self._df.iloc[row, col] = value
        column_name = self._df.columns[col]
        self._df_all[column_name][row] = value
        self.dataChanged.emit(self.index(row, col), self.index(row, col))

    @log_method
    def rename_column(self, column_index: int, new_name: str):
        if new_name in self._df_all.columns:
            logging.error("Column name already exists")
            return

        self.setHorizontalHeaderLabels(
            [new_name if i == column_index else self._df.columns[i] for i in range(self.columnCount())]
        )

    def get_column_name(self, column_index: int):
        assert 0 <= column_index < self.columnCount()
        return str(self._df.columns[column_index])

    def get_column_names(self) -> List[str]:
        return [str(column) for column in self._df.columns]

    @log_method
    def get_column(self, column_index: int):
        assert 0 <= column_index < self.columnCount()
        return self._df.iloc[:, column_index]

    @log_method
    def set_column(self, column_index: int, values: Union[List, pd.Series]):
        assert len(values) == self.rowCount()
        column_name = self._df.columns[column_index]
        self._df[column_name] = values
        self._df_all[column_name] = values
        self.dataChanged.emit(self.index(0, column_index), self.index(self.rowCount() - 1, column_index))

    @log_method_noarg
    def get_data(self):
        return self._df.copy()

    def get_column_flags(self, column_name: str):
        return self.column_flags[column_name]

    @log_method
    def set_column_flag(self, column_name: str, flag: str, value: bool):
        self.column_flags[column_name].set_flag(flag, value)
        self.headerDataChanged.emit(Qt.Horizontal, 0, self.columnCount())

    @log_method
    def toggle_column_flag(self, column_name: str, flag: str):
        self.set_column_flag(column_name, flag, not self.column_flags[column_name].get_flag(flag))
        self.headerDataChanged.emit(Qt.Horizontal, 0, self.columnCount())

    @log_method
    def get_column_dtype(self, column_index: int):
        if pd.api.types.is_integer_dtype(self._df.iloc[:, column_index]):
            return 'int'
        if pd.api.types.is_float_dtype(self._df.iloc[:, column_index]):
            return 'float'
        if pd.api.types.is_string_dtype(self._df.iloc[:, column_index]):
            return 'str'
        return 'other'

    @log_method
    def add_column(self, column_to_the_left_index):
        column_to_the_left_name = self.get_column_name(column_to_the_left_index)
        column_to_the_left_index_all = self._df_all.columns.get_loc(column_to_the_left_name)

        new_column_name = "New column "
        suffix = 1
        while new_column_name+str(suffix) in self._df_all.columns:
            suffix += 1
        new_column_name = "New column "+str(suffix)

        self.beginInsertColumns(QModelIndex(), column_to_the_left_index+1, column_to_the_left_index+1)
        self._df.insert(column_to_the_left_index+1, new_column_name, "")
        self._df_all.insert(column_to_the_left_index_all+1, new_column_name, "")
        self.column_flags[new_column_name] = ColumnFlags(self._df_all[new_column_name])
        self.endInsertColumns()

    @log_method
    def delete_column(self, column_index):
        column_name = self.get_column_name(column_index)
        self.beginRemoveColumns(QModelIndex(), column_index, column_index)
        self._df.drop(columns=[column_name], inplace=True)
        self._df_all.drop(columns=[column_name], inplace=True)
        self.column_flags.pop(column_name)
        self.endRemoveColumns()

    @log_method
    def delete_columns(self, column_indexes):
        column_names = [self.get_column_name(index) for index in column_indexes]
        self.beginRemoveColumns(QModelIndex(), min(column_indexes), max(column_indexes))
        self._df.drop(columns=column_names, inplace=True)
        self._df_all.drop(columns=column_names, inplace=True)
        for column_name in column_names:
            self.column_flags.pop(column_name)
        self.endRemoveColumns()

    def get_column_color(self, column_index):
        try:
            column_name = self.get_column_name(column_index)
            return self.column_flags[column_name].color
        except KeyError as e:
            logging.error(f"{self._df.columns=}")
            logging.error(f"{self._df_all.columns=}")
            logging.error(f"{self.column_flags=}")
            raise KeyError(e)

    @log_method
    def set_column_color(self, column_index, color):
        column_name = self.get_column_name(column_index)
        self.column_flags[column_name].color = color
        self.headerDataChanged.emit(Qt.Horizontal, column_index, column_index)