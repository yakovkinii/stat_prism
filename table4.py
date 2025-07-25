#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import random
import string
import sys

from PySide6 import QtCore, QtGui, QtWidgets


class ReadOnlyDelegate(QtWidgets.QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        if isinstance(editor, QtWidgets.QLineEdit):
            editor.setReadOnly(True)
            editor.setStyleSheet("border:1px solid gray;")
        return editor


class CustomHeader(QtWidgets.QHeaderView):
    class HeaderEditor(QtWidgets.QLineEdit):
        def __init__(self, text, parent):
            super().__init__(text, parent)
            self.setReadOnly(True)
            self.setStyleSheet("border:1px solid gray; background:white;")
            self.selectAll()

        def focusOutEvent(self, event):
            super().focusOutEvent(event)
            self.deleteLater()

    def __init__(self, orientation, parent):
        super().__init__(orientation, parent)
        self.setSectionsClickable(True)
        self._editor = None

    def mousePressEvent(self, event):
        # close any open editor
        table = self.parent()
        if hasattr(table, "_editingIndex") and table._editingIndex is not None:
            table.closePersistentEditor(table._editingIndex)
            table._editingIndex = None
        if self._editor:
            self._editor.deleteLater()
            self._editor = None
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        x = int(event.position().x())
        idx = self.logicalIndexAt(x)
        if idx >= 0:
            sx = self.sectionViewportPosition(idx)  # FIX: use viewport position
            sw = self.sectionSize(idx)
            rect = QtCore.QRect(sx, 0, sw, self.height())
            text = str(self.model().headerData(idx, self.orientation(), QtCore.Qt.DisplayRole))
            self._editor = CustomHeader.HeaderEditor(text, self)
            self._editor.setGeometry(rect.adjusted(2, 2, -2, -2))
            self._editor.show()
            self._editor.setFocus()
        else:
            super().mouseDoubleClickEvent(event)

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        bg = "#ccffcc" if logicalIndex == 2 else "white"
        painter.fillRect(rect, QtGui.QColor(bg))
        pen = QtGui.QPen(QtGui.QColor("lightgray"))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())
        text = self.model().headerData(logicalIndex, self.orientation(), QtCore.Qt.DisplayRole)
        painter.setPen(QtGui.QPen(QtGui.QColor("black")))
        painter.drawText(rect.adjusted(4, 0, -4, 0), QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, str(text))
        painter.restore()


class CopyableTableView(QtWidgets.QTableView):
    def __init__(self):
        super().__init__()
        self._editingIndex = None
        # allow partial cell horizontal scrolling
        self.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        # apply custom scrollbar styling in this widget
        self.setStyleSheet(
            """
            QTableView { font-size:10pt; color:black; background:white; border:none; outline:none; }
            QTableView::item { border-bottom:1px solid lightgray; }
            QScrollBar:vertical { width:6px; }
            QScrollBar:horizontal { height:6px; }
            QScrollBar::handle { background:#ccc; border-radius:3px; }
            QScrollBar::add-line, QScrollBar::sub-line { height:0; width:0; }
        """
        )

    def mousePressEvent(self, event):
        if self._editingIndex is not None:
            self.closePersistentEditor(self._editingIndex)
            self._editingIndex = None
        # clear header editor
        hdr = self.horizontalHeader()
        if hasattr(hdr, "_editor") and hdr._editor:
            hdr._editor.deleteLater()
            hdr._editor = None
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        idx = self.indexAt(event.position().toPoint())
        if idx.isValid():
            self.openPersistentEditor(idx)
            self._editingIndex = idx
        else:
            super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event):
        # On scroll, close any open cell editor
        if self._editingIndex is not None:
            self.closePersistentEditor(self._editingIndex)
            self._editingIndex = None
        # Also close header editor if open
        hdr = self.horizontalHeader()
        if hasattr(hdr, "_editor") and hdr._editor:
            hdr._editor.deleteLater()
            hdr._editor = None

        pos = event.position().toPoint()
        if pos.y() < self.horizontalHeader().height():
            delta = event.angleDelta().y() / 2  # slow horizontal scroll
            sb = self.horizontalScrollBar()
            sb.setValue(sb.value() - delta)
            event.accept()
        else:
            super().wheelEvent(event)


class TablePreviewPopup(QtWidgets.QWidget):
    def __init__(self, parent, model):
        super().__init__(parent, QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setGeometry(parent.rect())
        # semi-transparent overlay
        overlay = QtWidgets.QWidget(self)
        overlay.setGeometry(self.rect())
        overlay.setStyleSheet("background-color: rgba(0,0,0,0.3);")
        overlay.show()
        # popup container
        self.popup = QtWidgets.QFrame(self)
        w, h = int(parent.width() * 0.95), int(parent.height() * 0.95)
        self.popup.setFixedSize(w, h)
        self.popup.move((parent.width() - w) // 2, (parent.height() - h) // 2)
        self.popup.setStyleSheet("background:white;")
        self.popup.mousePressEvent = lambda e: e.accept()
        popup_layout = QtWidgets.QVBoxLayout(self.popup)
        popup_layout.setContentsMargins(0, 0, 0, 0)
        popup_layout.setSpacing(0)
        # padding widget
        padding_widget = QtWidgets.QWidget(self.popup)
        padding_layout = QtWidgets.QVBoxLayout(padding_widget)
        padding_layout.setContentsMargins(5, 5, 5, 5)
        padding_layout.setSpacing(0)
        # table
        table = CopyableTableView()
        self.setup_table(table, model)
        padding_layout.addWidget(table)
        popup_layout.addWidget(padding_widget)
        self.show()

    def setup_table(self, table, model):
        table.setModel(model)
        table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        table.setFocusPolicy(QtCore.Qt.NoFocus)
        table.verticalHeader().hide()
        table.setHorizontalHeader(CustomHeader(QtCore.Qt.Horizontal, table))
        table.horizontalHeader().setHighlightSections(False)
        table.setItemDelegate(ReadOnlyDelegate(table))
        table.setTextElideMode(QtCore.Qt.ElideRight)
        table.setWordWrap(False)
        table.setShowGrid(False)
        table.resizeColumnsToContents()
        table.resizeRowsToContents()

    def mousePressEvent(self, event):
        if not self.popup.geometry().contains(event.position().toPoint()):
            self.close()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.showMaximized()
        # full model
        self.full_model = self.create_model(50, 50)
        labels = [str(i + 1) for i in range(self.full_model.columnCount())]
        self.full_model.setHorizontalHeaderLabels(labels)
        # central
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        # preview model
        self.preview_model = QtGui.QStandardItemModel(5, 5)
        self.copy_model(self.full_model, self.preview_model, 5, 5)
        self.preview_model.setHorizontalHeaderLabels(labels[:5])
        # preview table
        self.preview_table = CopyableTableView()
        self.setup_table(self.preview_table, self.preview_model)
        self.preview_table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.preview_table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.preview_table.resizeColumnsToContents()
        self.preview_table.resizeRowsToContents()
        cols = self.preview_model.columnCount()
        rows = self.preview_model.rowCount()
        total_w = sum(self.preview_table.columnWidth(i) for i in range(cols))
        # Correct preview table height calculation
        header = self.preview_table.horizontalHeader()
        total_h = header.sizeHint().height()
        for i in range(rows):
            if not self.preview_table.isRowHidden(i):
                total_h += self.preview_table.rowHeight(i)
        # Add horizontal scroll bar height if visible
        if self.preview_table.horizontalScrollBar().isVisible():
            total_h += self.preview_table.horizontalScrollBar().height()
        # Add frame width if needed
        if self.preview_table.frameWidth():
            total_h += 2 * self.preview_table.frameWidth()
        self.preview_table.setFixedHeight(total_h)
        self.preview_table.setFixedWidth(total_w)
        # connect clicks to show full
        self.preview_table.clicked.connect(self.show_full)
        self.preview_table.horizontalHeader().sectionClicked.connect(self.show_full)
        layout.addWidget(self.preview_table, alignment=QtCore.Qt.AlignLeft)
        btn = QtWidgets.QPushButton("View Full Table")
        btn.clicked.connect(self.show_full)
        layout.addWidget(btn, alignment=QtCore.Qt.AlignRight)

    def create_model(self, rows, cols):
        model = QtGui.QStandardItemModel(rows, cols)
        for r in range(rows):
            for c in range(cols):
                text = "".join(random.choices(string.ascii_letters, k=random.randint(5, 20)))
                model.setItem(r, c, QtGui.QStandardItem(text))
        return model

    def copy_model(self, src, dest, rows, cols):
        for r in range(rows):
            for c in range(cols):
                dest.setItem(r, c, src.item(r, c).clone())

    def setup_table(self, table, model):
        table.setModel(model)
        table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        table.setFocusPolicy(QtCore.Qt.NoFocus)
        table.verticalHeader().hide()
        table.setHorizontalHeader(CustomHeader(QtCore.Qt.Horizontal, table))
        table.horizontalHeader().setHighlightSections(False)
        table.setItemDelegate(ReadOnlyDelegate(table))
        table.setTextElideMode(QtCore.Qt.ElideRight)
        table.setWordWrap(False)
        table.setShowGrid(False)

    def show_full(self):
        _ = TablePreviewPopup(self, self.full_model)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.showMaximized()
    sys.exit(app.exec())
