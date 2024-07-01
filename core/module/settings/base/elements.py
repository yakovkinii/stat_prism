from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget

from core.panels.common.common_ui import (
    create_tool_button_qta,
    create_label,
    create_label_editable,
    create_label_editable_wordwrap,
    create_tool_button,
)


# 30 ... 380


class Title:
    def __init__(self, parent_widget, label_text):
        self.widget = create_label(
            parent=parent_widget,
            label_geometry=None,
            font_size=12,
            alignment=QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter,
        )
        self.widget.setText(label_text)


class EditableTitle:
    def __init__(self, parent_widget, label_text, handler=None):
        self.widget = create_label_editable(
            parent=parent_widget,
            label_geometry=None,
            font_size=14,
            alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter,
        )
        self.widget.setText(label_text)
        if handler is not None:
            self.widget.editingFinished.connect(handler)


class EditableTitleWordWrap:
    def __init__(self, parent_widget, label_text, handler=None):
        self.widget = create_label_editable_wordwrap(
            parent=parent_widget,
            font_size=14,
            alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter,
        )
        # use only the needed vertical size

        self.widget.setText(label_text)
        if handler is not None:
            self.widget.editingFinished.connect(handler)


class BigAssButton:
    def __init__(self, parent_widget, label_text, icon_path, handler=None):
        self.widget = QWidget(parent_widget)
        self._margin = 30
        self._height = 101
        self.widget.setFixedHeight(self._height + self._margin)
        icon_path = icon_path if icon_path is not None else "msc.blank"

        self.button = create_tool_button_qta(
            parent=self.widget,
            button_geometry=QtCore.QRect(self._margin, self._margin, self._height, self._height),
            icon_path=icon_path,
            icon_size=QtCore.QSize(80, 80),
        )
        self.label = create_label(
            parent=self.widget,
            label_geometry=QtCore.QRect(150, self._margin, 231, self._height),
            font_size=14,
            alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter,
        )
        self.label.setText(label_text)

        if handler is not None:
            self.button.pressed.connect(handler)


class Spacer:
    def __init__(self, parent_widget):
        self.widget = QWidget(parent_widget)
        self.widget.setFixedHeight(50)
