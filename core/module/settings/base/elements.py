from PyQt5 import QtCore

from core.ui.common.common_ui import create_tool_button_qta, create_label, create_label_editable

# 30 ... 380

class Title:
    def __init__(self, parent_widget, label_text, handler=None):
        self.parent_widget = parent_widget
        self.label_text=label_text
        self.margin = 10
        self.height = 41

        self.label = None

    def place(self, current_height):
        self.label = create_label(
            parent=self.parent_widget,
            label_geometry=QtCore.QRect(30, current_height + self.margin, 351, self.height),
            font_size=14,
            alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter,
        )
        self.label.setText(self.label_text)

        return current_height + self.margin * 2 + self.height


class EditableTitle:
    def __init__(self, parent_widget, label_text, handler=None):
        self.parent_widget = parent_widget
        self.handler = handler
        self.label_text=label_text
        self.margin = 10
        self.height = 41

        self.label = None

    def place(self, current_height):
        self.label = create_label_editable(
            parent=self.parent_widget,
            label_geometry=QtCore.QRect(30, current_height + self.margin, 351, self.height),
            font_size=14,
            alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter,
        )
        self.label.setText(self.label_text)
        if self.handler is not None:
            self.label.editingFinished.connect(self.handler)

        return current_height + self.margin * 2 + self.height



class BigAssButton:
    def __init__(self, parent_widget, label_text, icon_path, handler=None):
        self.label_text = label_text
        self.icon_path = icon_path
        self.parent_widget = parent_widget
        self.handler = handler

        self.margin = 10
        self.height = 101

        self.button = None
        self.label = None

    def place(self, current_height):
        self.button = create_tool_button_qta(
            parent=self.parent_widget,
            button_geometry=QtCore.QRect(30, current_height + self.margin, self.height, self.height),
            icon_path=self.icon_path,
            icon_size=QtCore.QSize(80, 80),
        )
        self.label = create_label(
            parent=self.parent_widget,
            label_geometry=QtCore.QRect(150, current_height + self.margin, 231, self.height),
            font_size=14,
            alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter,
        )
        self.label.setText(self.label_text)
        if self.handler is not None:
            self.button.pressed.connect(self.handler)

        return current_height + self.margin * 2 + self.height



class Spacer:
    def __init__(self, parent_widget):
        self.parent_widget = parent_widget
        self.height = 150

    def place(self, current_height):
        return current_height + self.height
