from PySide6 import QtCore, QtGui
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHeaderView,
    QLineEdit,
    QStyledItemDelegate,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from src.data.data import Data
from src.pyside_ext.markup import css
from src.pyside_ext.unique_qss import set_stylesheet


def view_data_popup(root_class, data: Data):
    df = data.dataframe
    model = QtGui.QStandardItemModel(len(df), len(df.columns))
    for r in range(len(df)):
        for c in range(len(df.columns)):
            item = QtGui.QStandardItem(str(df.iat[r, c]))
            model.setItem(r, c, item)
    model.setHorizontalHeaderLabels(df.columns.tolist())

    TablePopup(root_class, model)


class ReadOnlyDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        if isinstance(editor, QLineEdit):
            editor.setReadOnly(True)
            set_stylesheet(editor, css(border="1px solid gray"))
        return editor


class CustomHeader(QHeaderView):
    class HeaderEditor(QLineEdit):
        def __init__(self, text, parent):
            super().__init__(text, parent)
            self.setReadOnly(True)
            set_stylesheet(self, css(border="1px solid gray", background="white"))
            self.selectAll()

        def focusOutEvent(self, event):
            super().focusOutEvent(event)
            self.deleteLater()

    def __init__(self, orientation, parent):
        super().__init__(orientation, parent)
        self.setSectionsClickable(True)
        self._editor = None

    def mousePressEvent(self, event):
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
            sx = self.sectionViewportPosition(idx)
            sw = self.sectionSize(idx)
            rect = QtCore.QRect(sx, 0, sw, self.height())
            text = str(self.model().headerData(idx, self.orientation(), QtCore.Qt.DisplayRole))
            self._editor = self.HeaderEditor(text, self)
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


class DataTableView(QTableView):
    def __init__(self):
        super().__init__()
        self._editingIndex = None
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
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
        if self._editingIndex is not None:
            self.closePersistentEditor(self._editingIndex)
            self._editingIndex = None
        hdr = self.horizontalHeader()
        if hasattr(hdr, "_editor") and hdr._editor:
            hdr._editor.deleteLater()
            hdr._editor = None

        pos = event.position().toPoint()
        if pos.y() < self.horizontalHeader().height():
            delta = event.angleDelta().y() / 2
            sb = self.horizontalScrollBar()
            sb.setValue(sb.value() - delta)
            event.accept()
        else:
            super().wheelEvent(event)


class TablePopup(QWidget):
    def __init__(self, parent, model):
        super().__init__(parent, QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setGeometry(parent.rect())

        overlay = QWidget(self)
        overlay.setGeometry(self.rect())
        overlay.setStyleSheet("background-color: rgba(0,0,0,0.3);")
        overlay.show()

        self.popup = QFrame(self)
        w, h = int(parent.width() * 0.95), int(parent.height() * 0.95)
        self.popup.setFixedSize(w, h)
        self.popup.move((parent.width() - w) // 2, (parent.height() - h) // 2)
        self.popup.setStyleSheet(css(background="white"))
        self.popup.mousePressEvent = lambda e: e.accept()

        popup_layout = QVBoxLayout(self.popup)
        popup_layout.setContentsMargins(0, 0, 0, 0)
        popup_layout.setSpacing(0)

        padding_widget = QWidget(self.popup)
        padding_layout = QVBoxLayout(padding_widget)
        padding_layout.setContentsMargins(5, 5, 5, 5)
        padding_layout.setSpacing(0)

        table = DataTableView()
        self._setup_table(table, model)
        padding_layout.addWidget(table)
        popup_layout.addWidget(padding_widget)
        self.show()

    def _setup_table(self, table, model):
        table.setModel(model)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.NoSelection)
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

        min_width = 80
        max_width = 300
        for col in range(model.columnCount()):
            table.setColumnWidth(col, max(min_width, min(table.columnWidth(col), max_width)))

    def mousePressEvent(self, event):
        if not self.popup.geometry().contains(event.position().toPoint()):
            self.close()
