#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import sys
import random
import string
from PySide6 import QtWidgets, QtCore, QtGui

class TablePreviewPopup(QtWidgets.QWidget):
    def __init__(self, parent, model):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setGeometry(parent.rect())  # overlay covers main window

        # Popup frame at 95% size
        self.popup = QtWidgets.QFrame(self)
        w = int(parent.width() * 0.95)
        h = int(parent.height() * 0.95)
        self.popup.setFixedSize(w, h)
        self.popup.move((parent.width() - w) // 2, (parent.height() - h) // 2)
        self.popup.setStyleSheet('background-color: white; border-radius: 8px;')
        self.popup.mousePressEvent = lambda event: event.accept()

        layout = QtWidgets.QVBoxLayout(self.popup)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.table = QtWidgets.QTableView()
        self.table.setModel(model)
        self.apply_style(self.table)
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        layout.addWidget(self.table)

        self.show()

    def apply_style(self, table):
        table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        table.setFocusPolicy(QtCore.Qt.NoFocus)  # disable focus rectangle
        table.verticalHeader().hide()
        table.horizontalHeader().setHighlightSections(False)
        table.setTextElideMode(QtCore.Qt.ElideRight)
        table.setWordWrap(False)
        table.setShowGrid(False)
        table.setStyleSheet('''
            QTableView { font-size:10pt; color:black; background:white; border:none; outline: none; }
            QHeaderView::section { background:white; border:none; border-bottom:2px solid lightgray; font-size:10pt; }
            QTableView::item { border-bottom:1px solid lightgray; }
            QScrollBar:vertical { width:6px; }
            QScrollBar:horizontal { height:6px; }
            QScrollBar::handle { background:#ccc; border-radius:3px; }
            QScrollBar::add-line, QScrollBar::sub-line { height:0px; width:0px; }
        ''')

    def mousePressEvent(self, event):
        if not self.popup.geometry().contains(event.pos()):
            self.close()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.showMaximized()

        self.full_model = self.create_model(50, 50)
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Prepare preview slice
        self.preview_model = QtGui.QStandardItemModel(5, 5)
        self.copy_model(self.full_model, self.preview_model, 5, 5)

        self.preview_table = QtWidgets.QTableView()
        self.apply_style(self.preview_table)
        self.preview_table.setModel(self.preview_model)
        self.preview_table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.preview_table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.preview_table.resizeColumnsToContents()
        self.preview_table.resizeRowsToContents()

        cols = self.preview_model.columnCount()
        rows = self.preview_model.rowCount()
        total_w = sum(self.preview_table.columnWidth(i) for i in range(cols))
        total_h = self.preview_table.horizontalHeader().height() + sum(self.preview_table.rowHeight(i) for i in range(rows))
        self.preview_table.setFixedSize(total_w, total_h)

        layout.addWidget(self.preview_table, alignment=QtCore.Qt.AlignLeft)

        btn = QtWidgets.QPushButton('View Full Table')
        btn.clicked.connect(self.show_full)
        layout.addWidget(btn, alignment=QtCore.Qt.AlignRight)

    def create_model(self, rows, cols):
        model = QtGui.QStandardItemModel(rows, cols)
        for r in range(rows):
            for c in range(cols):
                text = ''.join(random.choices(string.ascii_letters, k=random.randint(5, 20)))
                model.setItem(r, c, QtGui.QStandardItem(text))
        return model

    def copy_model(self, src, dest, rows, cols):
        for r in range(rows):
            for c in range(cols):
                dest.setItem(r, c, src.item(r, c).clone())

    def apply_style(self, table):
        table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        table.setFocusPolicy(QtCore.Qt.NoFocus)
        table.verticalHeader().hide()
        table.horizontalHeader().setHighlightSections(False)
        table.setTextElideMode(QtCore.Qt.ElideRight)
        table.setWordWrap(False)
        table.setShowGrid(False)
        table.setStyleSheet('''
            QTableView { font-size:10pt; color:black; background:white; border:none; outline: none; }
            QHeaderView::section { background:white; border:none; border-bottom:2px solid lightgray; font-size:10pt; }
            QTableView::item { border-bottom:1px solid lightgray; }
            QScrollBar:vertical { width:6px; }
            QScrollBar::handle { background:#ccc; border-radius:3px; }
            QScrollBar::add-line, QScrollBar::sub-line { height:0px; width:0px; }
        ''')

    def show_full(self):
        # semi-transparent black overlay
        overlay = QtWidgets.QWidget(self)
        overlay.setGeometry(self.rect())
        overlay.setStyleSheet('background-color: rgba(0, 0, 0, 0.3);')
        overlay.show()
        popup = TablePreviewPopup(self, self.full_model)
        popup.destroyed.connect(overlay.deleteLater)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())
