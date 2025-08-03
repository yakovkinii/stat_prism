#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from PySide6 import QtCore
from PySide6.QtWidgets import QLabel

from src.pyside_ext.styling import Style


class ResultLabel(QLabel):
    def __init__(self, parent, label_text):
        super().__init__(parent)
        self.setText(label_text)
        self.setFont(Style.font_result_label)
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
