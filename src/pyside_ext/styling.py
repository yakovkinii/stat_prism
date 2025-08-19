#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from enum import Enum

from PySide6 import QtGui

_font_regular = QtGui.QFont("Segoe UI")
_font_regular.setPointSize(12)

_font_result_label = QtGui.QFont("Segoe UI")
_font_result_label.setPointSize(16)

_font_result_element_label = QtGui.QFont("Segoe UI")
_font_result_element_label.setPointSize(10)


class Style:
    font_regular = _font_regular
    font_result_label = _font_result_label
    font_result_element_label = _font_result_element_label

    class Color(Enum):
        def __str__(self):
            return str(self.value)

        BackgroundElevated = "#eee"
        BackgroundEdit = "#fff"
        Background = "#fff"
        BackgroundNotSelected = "#f5f5f5"
        BorderElevated = "#ccc"
        Border = "#eee"
        Highlight = "#05f"
        Danger = "#700"
        Text = "#000"
        SimpleToolButton = "#888"

    class FontFamily(Enum):
        def __str__(self):
            return str(self.value)

        SegoeUI = "Segoe UI"

    class FontSize(Enum):
        def __str__(self):
            return str(self.value)

        smaller = "10pt"
        regular = "12pt"
        larger = "14pt"

    class General(Enum):
        def __str__(self):
            return str(self.value)

        border = "1px solid"
        border_data_analysis = "5px solid #aaf"  # Todo deprecate
        border_data_processing = "5px solid #afa"  # Todo deprecate
        border_thick_unselected = "5px solid #eee"
        border_thick_selected = "5px solid #05f"
        border_thin_unselected = "2px solid #eee"
        border_thin_selected = "2px solid #05f"
