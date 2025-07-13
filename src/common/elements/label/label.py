#
#  Copyright (c) 2023 -- 2025 StatPrism Team. All rights reserved.
#

from PySide6 import QtCore, QtGui, QtWidgets

from src.common.elements.base.base import BasePanelElement


class Label(BasePanelElement):
    def __init__(self, label_text):
        super().__init__()
        self.label_text = label_text

    def setup(self):
        self.widget = QtWidgets.QLabel(self.parent_widget)
        self.widget.setWordWrap(True)
        self.widget.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        font = QtGui.QFont("Segoe UI")
        font.setPointSize(8)
        self.widget.setFont(font)
        self.widget.setText(self.label_text)
