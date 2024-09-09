from PySide6 import QtCore, QtGui, QtWidgets

from src.common.elements.base.base import BasePanelElement


class Title(BasePanelElement):
    def __init__(self, label_text):
        super().__init__()
        self.label_text = label_text

    def setup(self):
        self.widget = QtWidgets.QLabel(self.parent_widget)
        # font = QtGui.QFont("Freestyle Script")
        font = QtGui.QFont("Segoe UI")
        font.setPointSize(12)
        self.widget.setFont(font)
        self.widget.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.widget.setText(self.label_text)
