import qtawesome as qta
from PyQt5 import QtCore, QtGui, QtWidgets

import resources_rc


def icon(path):
    _icon = QtGui.QIcon()
    _icon.addPixmap(
        QtGui.QPixmap(path),
        QtGui.QIcon.Normal,
        QtGui.QIcon.Off,
    )
    return _icon


def add_checkbox_to_groupbox(groupBox, i, formLayout):
    checkbox = QtWidgets.QCheckBox(groupBox)
    checkbox.setChecked(True)
    formLayout.setWidget(i, QtWidgets.QFormLayout.LabelRole, checkbox)
    return checkbox


def create_tool_button(parent, button_geometry, icon_path, icon_size):
    button = QtWidgets.QToolButton(parent)
    button.setGeometry(button_geometry)
    button.setText("")
    button.setIcon(icon(icon_path))
    button.setIconSize(icon_size)
    button.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
    return button


def create_tool_button_qta(parent, button_geometry, icon_path, icon_size):
    button = QtWidgets.QToolButton(parent)
    button.setGeometry(button_geometry)
    button.setText("")
    button.setIcon(qta.icon(icon_path))
    button.setIconSize(icon_size)
    button.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
    return button


def create_label(parent, label_geometry, font_size, alignment):
    label = QtWidgets.QLabel(parent)
    label.setGeometry(label_geometry)
    font = QtGui.QFont("Segoe UI")
    font.setPointSize(font_size)
    label.setFont(font)
    label.setAlignment(alignment)
    return label


if __name__ == "__main__":
    _ = resources_rc
