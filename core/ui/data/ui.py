import logging
from typing import TYPE_CHECKING

import pandas as pd
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QVBoxLayout

from core.globals.data import data, Data
from core.globals.debug import DEBUG_LAYOUT
from core.ui.data.table.header.ui import LeftAlignHeaderView
from core.ui.data.table.ui import CustomTableWidget
from core.registry.utility import log_method, log_method_noarg, num_to_str

if TYPE_CHECKING:
    from core.ui.ui import MainWindowClass


class DataPanelClass:
    def __init__(self, parent_widget, parent_class, root_class):
        # Setup
        self.root_class: MainWindowClass = root_class
        self.parent_class: MainWindowClass = parent_class
        self.widget = QtWidgets.QWidget(parent_widget)
        if DEBUG_LAYOUT:
            self.widget.setStyleSheet("border: 1px solid blue; background-color: #eef;")
        self.widget_layout = QVBoxLayout(self.widget)
        self.widget_layout.setContentsMargins(0, 0, 0, 0)
        self.widget.setLayout(self.widget_layout)

        # Definition

        self.table = CustomTableWidget(self.widget)
        self.widget_layout.addWidget(self.table)

        self.table.setAutoFillBackground(False)
        self.table.setFrameShape(QtWidgets.QFrame.NoFrame)
        # self.table.setAlternatingRowColors(True)
        # self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        # self.table.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.table.setShowGrid(True)
        self.table.setGridStyle(QtCore.Qt.SolidLine)
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        self.header = LeftAlignHeaderView(QtCore.Qt.Horizontal, self.table)
        self.table.setHorizontalHeader(self.header)

        self.table.horizontalHeader().setVisible(True)
        self.table.horizontalHeader().setCascadingSectionResizes(False)
        self.table.verticalHeader().setVisible(True)
        self.table.verticalHeader().setCascadingSectionResizes(False)
        self.table.verticalHeader().setHighlightSections(True)
        self.table.verticalHeader().setSortIndicatorShown(False)
        self.table.verticalHeader().setStretchLastSection(False)

        self.table.selectionModel().selectionChanged.connect(self.on_selection_changed)
        self.update()

    @log_method
    def on_selection_changed(self, selected, deselected):
        # This method will be called whenever the selection changes
        selected_columns = list({index.column() for index in self.table.selectedIndexes()})
        if len(selected_columns) == 1:
            self.root_class.action_activate_column_panel(selected_columns[0])
        logging.debug(f"Selected columns: {selected_columns}")

    def retranslateUI(self):
        pass

    @log_method_noarg
    def update(self):
        self.load_data_to_table(data)

    @log_method
    def load_data_to_table(self, data:Data):
        self.table.setRowCount(data.df.shape[0])
        self.table.setColumnCount(data.df.shape[1])
        self.table.setHorizontalHeaderLabels([column_info.display_name for column_info in data.column_info])
        for i in range(self.table.columnCount()):
            self.table.setColumnWidth(i, 170)

        for row in data.df.iterrows():
            for col, value in enumerate(row[1]):
                item = QTableWidgetItem(num_to_str(value))
                # item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                self.table.setItem(row[0], col, item)


