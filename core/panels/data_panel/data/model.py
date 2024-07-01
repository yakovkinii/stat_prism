import logging
from typing import Union, List, Dict
import qtawesome as qta
import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtCore import QAbstractTableModel, Qt
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



        self.beginResetModel()
        self._df_all = dataframe
        self._df = dataframe
        self.column_flags = {}
        for column in dataframe.columns:
            self.column_flags[column] = ColumnFlags(
                dataframe[column]
            )
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
                icons.append(qta.icon('fa.asl-interpreting'))

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
        logging.warning("setHorizontalHeaderLabels called")
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

    @log_method
    def get_column_name(self, column_index: int):
        assert 0 <= column_index < self.columnCount()
        return str(self._df.columns[column_index])

    @log_method_noarg
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
