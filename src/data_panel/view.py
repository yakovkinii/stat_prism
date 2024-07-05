import logging

from PyQt5 import QtCore
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QTableView


class DataView(QTableView):
    copy_signal = QtCore.pyqtSignal(int)
    paste_signal = QtCore.pyqtSignal(int)
    def __init__(self, parent=None):
        super(DataView, self).__init__(parent)
        palette = self.palette()
        palette.setColor(QPalette.Highlight, QColor(240, 240, 240))  # Change to the color you want
        palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        self.setPalette(palette)

    def wheelEvent(self, event):
        if event.angleDelta().y() != 0 and self.horizontalHeader().underMouse():
            # Translate vertical scrolling to horizontal
            delta = event.angleDelta().y() / 100
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta)
            event.accept()  # Accept the event to prevent default handling
        else:
            super().wheelEvent(event)  # Default behavior for other cases

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_C and event.modifiers() == QtCore.Qt.ControlModifier:
            self.copy_signal.emit(event.key())
            # stop propagation
            event.accept()
            return
        if event.key() == QtCore.Qt.Key_V and event.modifiers() == QtCore.Qt.ControlModifier:
            self.paste_signal.emit(event.key())
            event.accept()
            return


        super().keyPressEvent(event)

