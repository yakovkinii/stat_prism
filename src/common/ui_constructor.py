import qtawesome as qta
from PySide6 import QtCore, QtGui, QtWidgets

import resources_rc
from src.common.subclassed_widgets import EditableLabelWordwrap


def icon(path):
    _icon = QtGui.QIcon()
    _icon.addPixmap(
        QtGui.QPixmap(path),
        QtGui.QIcon.Mode.Normal,
        QtGui.QIcon.State.Off,
    )
    return _icon


def create_tool_button_qta(parent, button_geometry, icon_path, icon_size):
    button = QtWidgets.QToolButton(parent)
    button.setGeometry(button_geometry)
    button.setText("")

    button.setIcon(qta.icon(icon_path))
    button.setIconSize(icon_size)
    button.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly)
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


def create_label_editable_wordwrap(parent, font_size, alignment):
    label = EditableLabelWordwrap(parent)
    font = QtGui.QFont("Segoe UI")
    font.setPointSize(font_size)
    label.setFont(font)
    label.setAlignment(alignment)
    return label


if __name__ == "__main__":
    _ = resources_rc
