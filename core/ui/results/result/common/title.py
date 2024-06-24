from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt

from core.ui.results.result.common.label import LabelClickable
from core.registry.utility import log_method


class TitleWidget(LabelClickable):
    @log_method
    def __init__(self, parent, text, size=8, centered=False):
        super().__init__(parent)
        self.setWordWrap(True)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.setAlignment(QtCore.Qt.AlignCenter if centered else QtCore.Qt.AlignLeft)
        font = QtGui.QFont("Segoe UI")
        font.setPointSize(size)

        palette = self.palette()
        palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(0, 0, 80))

        self.setPalette(palette)

        self.setFont(font)
        self.setText(text)
