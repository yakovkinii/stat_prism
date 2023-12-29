import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import (QApplication, QHeaderView, QMenu, QTableWidget,
                             QTableWidgetItem)


class CustomHeaderView(QHeaderView):
    def __init__(self, orientation, parent=None):
        super(CustomHeaderView, self).__init__(orientation, parent)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        getColAction = menu.addAction("Get Column Name/Number")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == getColAction:
            self.getColumn()

    def getColumn(self):
        logicalIndex = self.logicalIndexAt(self.mapFromGlobal(QCursor.pos()))
        # Print or process the column number/name
        print("Selected Column:", logicalIndex)
        # If you have headers and want names, you can use self.model().headerData(logicalIndex, Qt.Horizontal).toString()


class CustomTableWidget(QTableWidget):
    def __init__(self, *args):
        super().__init__(*args)
        self.setHorizontalHeader(CustomHeaderView(Qt.Horizontal, self))
        self.initUI()

    def initUI(self):
        # Example data
        # for i in range(self.rowCount()):
        #     for j in range(self.columnCount()):
        #         self.setItem(i, j, QTableWidgetItem(f"Item {i},{j}"))
        ...

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        getColsAction = menu.addAction("Get Selected Columns")

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == getColsAction:
            self.getSelectedColumns()

    def getSelectedColumns(self):
        selectedRanges = self.selectedRanges()
        columns = set()
        for rng in selectedRanges:
            for col in range(rng.leftColumn(), rng.rightColumn() + 1):
                columns.add(col)

        # Print or process the column numbers/names
        print("Selected Columns:", columns)
        # If you have headers and want names, you can use self.horizontalHeaderItem(col).text()
