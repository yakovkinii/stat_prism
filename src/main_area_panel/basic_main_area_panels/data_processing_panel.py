#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import random
import string

import attrs
import pandas as pd
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QLabel, QHBoxLayout

from src.common.elements.button.large_button import LargeButton
from src.common.elements.label.label import Label
from src.common.elements.utility.layout_helpers import empty_widget
from src.pyside_ext.layout import VBoxLayout, HBoxLayout
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet

import qtawesome as qta
@attrs.define()
class DataProcessingConfig:
    unique_id: int
    caption: str
    dataframe: pd.DataFrame  # Will be data model


class DataProcessing:
    def __init__(self, config: DataProcessingConfig, parent_widget, parent_class, root_class):
        self.config = config
        self.parent_widget = parent_widget
        self.parent_class = parent_class
        self.root_class = root_class

        self.full_model = self.create_model(self.config.dataframe)

        self.table_window = TableWindow(parent_widget=parent_widget, root_class=root_class, full_model=self.full_model,
                                  )

        self.widget, self.layout = empty_widget(
            parent=parent_widget,
            inner_layout_class=QHBoxLayout,
        )
        set_stylesheet(self.widget, css(background_color=Style.Color.BackgroundElevated))

        self.title = QLabel(self.config.caption)
        set_stylesheet(
            self.title,
            css(
                font_family=Style.FontFamily.SegoeUI,
                font_size=Style.FontSize.larger,
                text_align="left",
                margin="5px"
            ),
        )
        # self.title.setup()
        self.layout.addWidget(self.title)

        self.layout.addWidget(self.table_window.button)
        self.layout.addStretch()

    def create_model(self, df: pd.DataFrame):
        # model = QtGui.QStandardItemModel(rows, cols)
        # for r in range(rows):
        #     for c in range(cols):
        #         text = "".join(random.choices(string.ascii_letters, k=random.randint(5, 20)))
        #         model.setItem(r, c, QtGui.QStandardItem(text))

        model = QtGui.QStandardItemModel(len(df), len(df.columns))
        for r in range(len(df)):
            for c in range(len(df.columns)):
                item = QtGui.QStandardItem(str(df.iat[r, c]))
                model.setItem(r, c, item)

        # Set the header labels
        model.setHorizontalHeaderLabels(df.columns.tolist())


        return model

    def copy_model(self, src, dest, rows, cols):
        for r in range(rows):
            for c in range(cols):
                dest.setItem(r, c, src.item(r, c).clone())


class TableWindow(QtWidgets.QWidget):
    def __init__(
            self,
            parent_widget,
            root_class,
            full_model,
    ):
        super().__init__(parent_widget)
        self.root_class = root_class

        # full model
        self.full_model = full_model

        self.button = QtWidgets.QPushButton()
        set_stylesheet(
            self.button,
            css(
                margin_top="2px",
                font_family=Style.FontFamily.SegoeUI,
                font_size=Style.FontSize.larger,
                text_align="left",
                border=Style.General.border,
                border_color=Style.Color.BorderElevated,
            ),
            css(
                "#id:hover",
                border_color=Style.Color.Highlight,
            ),
        )
        icon = qta.icon("msc.table")
        self.button.setIcon(icon)
        self.button.setIconSize(QSize(60, 60))
        self.button.setFixedHeight(60)
        self.button.setFixedWidth(60)
        self.button.clicked.connect(self.show_full)

    def show_full(self):
        _ = TablePreviewPopup(self.root_class, self.full_model)


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


