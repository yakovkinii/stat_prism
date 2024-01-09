from typing import TYPE_CHECKING

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem

from core.mainwindow.data.table.header.ui import LeftAlignHeaderView
from core.mainwindow.data.table.ui import CustomTableWidget
from core.shared import data
from core.utility import log_method, log_method_noarg, num_to_str

if TYPE_CHECKING:
    from core.mainwindow.ui import MainWindow


class Data:
    def __init__(self, parent, mainwindow_instance):
        self.mainwindow_instance: MainWindow = mainwindow_instance

        self.table = CustomTableWidget(parent)
        self.table.setAutoFillBackground(False)
        self.table.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.table.setAlternatingRowColors(True)
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

    def retranslateUI(self):
        pass

    @log_method_noarg
    def update(self):
        self.load_data_to_table(data.df)

    @log_method
    def load_data_to_table(self, dataframe):
        self.table.setRowCount(dataframe.shape[0])
        self.table.setColumnCount(dataframe.shape[1])
        self.table.setHorizontalHeaderLabels(dataframe.columns)

        for row in dataframe.iterrows():
            for col, value in enumerate(row[1]):
                item = QTableWidgetItem(num_to_str(value))
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                self.table.setItem(row[0], col, item)
