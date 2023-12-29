from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

from core.shared import data
from core.utility import log_method_noarg, log_method


class Table:
    def __init__(self, parent):
        self.tableWidget_2 = QTableWidget(parent)
        self.tableWidget_2.setMinimumSize(QtCore.QSize(50, 0))
        self.tableWidget_2.setAutoFillBackground(False)
        self.tableWidget_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.tableWidget_2.setAlternatingRowColors(True)
        self.tableWidget_2.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.tableWidget_2.setHorizontalScrollMode(
            QtWidgets.QAbstractItemView.ScrollPerPixel
        )
        self.tableWidget_2.setShowGrid(True)
        self.tableWidget_2.setGridStyle(QtCore.Qt.SolidLine)
        self.tableWidget_2.setRowCount(0)
        self.tableWidget_2.setColumnCount(0)
        self.tableWidget_2.setObjectName("tableWidget_2")
        self.tableWidget_2.horizontalHeader().setVisible(True)
        self.tableWidget_2.horizontalHeader().setCascadingSectionResizes(False)
        self.tableWidget_2.verticalHeader().setVisible(True)
        self.tableWidget_2.verticalHeader().setCascadingSectionResizes(False)
        self.tableWidget_2.verticalHeader().setHighlightSections(True)
        self.tableWidget_2.verticalHeader().setSortIndicatorShown(False)
        self.tableWidget_2.verticalHeader().setStretchLastSection(False)

    def retranslateUI(self):
        pass

    @log_method_noarg
    def update(self):
        self.load_data_to_table(data.df)

    @log_method
    def load_data_to_table(self, dataframe):
        self.tableWidget_2.setRowCount(dataframe.shape[0])
        self.tableWidget_2.setColumnCount(dataframe.shape[1])
        self.tableWidget_2.setHorizontalHeaderLabels(dataframe.columns)

        for row in dataframe.iterrows():
            for col, value in enumerate(row[1]):
                self.tableWidget_2.setItem(row[0], col, QTableWidgetItem(str(value)))

