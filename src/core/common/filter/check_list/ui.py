from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAbstractItemView, QListWidget

from src.common.registry import log_method


class CheckListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setMouseTracking(True)
        self._fillingState = None
        self.start_item = None
        self.start_item_check_state = None

    @log_method
    def add_item_custom(self, item, checkable=True, checked=False):
        if checkable:
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
        else:
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
        self.addItem(item)

    @log_method
    def mousePressEvent(self, event):
        # super().mousePressEvent(event)
        item = self.itemAt(event.pos())
        if item:
            button = event.button()
            if button == Qt.LeftButton:
                self._fillingState = Qt.Checked
            elif button == Qt.RightButton:
                self._fillingState = Qt.Unchecked
            else:
                return
            self.start_item = item
            self.start_item_check_state = item.checkState()
            self.toggleCheckState(item)

    @log_method
    def mouseDoubleClickEvent(self, event):
        self.mousePressEvent(event)

    @log_method
    def mouseReleaseEvent(self, event):
        item = self.itemAt(event.pos())
        # super().mouseReleaseEvent(event)

        if item == self.start_item and (item.flags() & Qt.ItemIsEnabled) and (event.button() == Qt.LeftButton):
            item.setCheckState(Qt.Checked if self.start_item_check_state == Qt.Unchecked else Qt.Unchecked)

        self._fillingState = None

    @log_method
    def mouseMoveEvent(self, event):
        if self._fillingState is not None:
            item = self.itemAt(event.pos())
            if item:
                self.toggleCheckState(item)
        # super().mouseMoveEvent(event)

    @log_method
    def toggleCheckState(self, item):
        if self._fillingState is None:
            return
        if item.flags() & Qt.ItemIsEnabled:
            item.setCheckState(self._fillingState)
