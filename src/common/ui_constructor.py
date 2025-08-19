#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import qtawesome as qta
from PySide6 import QtCore, QtGui, QtWidgets

import resources_rc
from src.pyside_ext.elements.utility.primitive_elements import EditableLabelWordwrap
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet


def icon(path):
    _icon = QtGui.QIcon()
    _icon.addPixmap(
        QtGui.QPixmap(path),
        QtGui.QIcon.Mode.Normal,
        QtGui.QIcon.State.Off,
    )
    return _icon


def create_tool_button_qta(parent, icon_path, icon_size, button_geometry=None, **kwargs):
    button = QtWidgets.QToolButton(parent)
    if button_geometry is not None:
        button.setGeometry(button_geometry)
    button.setText("")

    button.setIcon(qta.icon(icon_path, **kwargs))
    button.setIconSize(icon_size)
    button.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly)
    return button


def create_simple_tool_button_qta(parent, icon_path, icon_size, color=None):
    button = QtWidgets.QToolButton(parent)
    button.setText("")
    if color is None:
        color = Style.Color.SimpleToolButton.value
    button.setIcon(qta.icon(icon_path, color=color))
    button.setIconSize(icon_size)
    button.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly)
    set_stylesheet(
        button,
        css(
            background_color="transparent",
            border="none",
        ),
    )
    return button


def create_label(parent, label_geometry, font_size, alignment):
    label = QtWidgets.QLabel(parent)
    if label_geometry is not None:
        label.setGeometry(label_geometry)
    font = QtGui.QFont("Segoe UI")
    font.setPointSize(font_size)
    label.setFont(font)
    label.setAlignment(alignment)
    return label


def create_label_editable_wordwrap(parent, alignment):
    label = EditableLabelWordwrap(parent)
    label.setFont(Style.font_regular)
    label.setAlignment(alignment)
    return label


if __name__ == "__main__":
    _ = resources_rc
