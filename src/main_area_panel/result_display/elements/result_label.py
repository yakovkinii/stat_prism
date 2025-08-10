#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from PySide6 import QtCore

from src.pyside_ext.elements.utility.primitive_elements import QLabelClickable
from src.pyside_ext.styling import Style


class ResultLabel(QLabelClickable):
    def __init__(self, parent, label_text):
        super().__init__(parent)
        self.setText(label_text)
        self.setFont(Style.font_result_label)
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
