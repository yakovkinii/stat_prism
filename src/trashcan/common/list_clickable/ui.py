from PyQt5 import QtCore
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QListWidget


class CustomListWidget(QListWidget):
    clicked = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)
        self.clicked.emit()
