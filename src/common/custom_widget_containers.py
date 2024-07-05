import qtawesome as qta
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout, QListWidgetItem, QWidget

from src.common.constant import COLORS
from src.common.subclassed_widgets import CheckListWidget
from src.common.ui_constructor import (
    create_label,
    create_label_editable,
    create_label_editable_wordwrap,
    create_tool_button_qta,
)
from src.common.unique_qss import set_stylesheet


class Title:
    def __init__(self, parent_widget, label_text):
        self.widget = create_label(
            parent=parent_widget,
            label_geometry=None,
            font_size=10,
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
            font_size=12,
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
        else:
            self.widget.setEnabled(False)
        self.button.pressed.connect(lambda: self.button.setDown(False))


class MediumAssButton:
    def __init__(self, parent_widget, label_text, icon_path, handler=None):
        self.widget = QWidget(parent_widget)
        self._margin_left = 30
        self._margin = 10
        self._height = 51
        self.widget.setFixedHeight(self._height + self._margin)
        icon_path = icon_path if icon_path is not None else "msc.blank"

        self.button = create_tool_button_qta(
            parent=self.widget,
            button_geometry=QtCore.QRect(self._margin_left, self._margin, self._height, self._height),
            icon_path=icon_path,
            icon_size=QtCore.QSize(40, 40),
        )
        self.label = create_label(
            parent=self.widget,
            label_geometry=QtCore.QRect(100, self._margin, 231, self._height),
            font_size=10,
            alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter,
        )
        self.label.setText(label_text)

        if handler is not None:
            self.button.pressed.connect(handler)
        else:
            self.widget.setEnabled(False)
        self.button.pressed.connect(lambda: self.button.setDown(False))


class Spacer:
    def __init__(self, parent_widget):
        self.widget = QWidget(parent_widget)
        self.widget.setFixedHeight(50)


class ColumnColorSelector:
    def __init__(self, parent_widget, handler=None):
        self.widget = QWidget(parent_widget)
        self.layout = QGridLayout(self.widget)

        self.buttons = []

        def get_handler(index):
            return lambda: handler(index)

        for i, color in enumerate(COLORS):
            button = QtWidgets.QToolButton(self.widget)
            button.setFixedWidth(40)
            button.setFixedHeight(40)
            button.setText("")
            set_stylesheet(button,"#id{"+f"background-color: {color}"+"}")
            button.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
            self.buttons.append(button)
            self.layout.addWidget(button, i // 6, i % 6)
            button.pressed.connect(get_handler(i))


class InvertVisualizer:
    def __init__(self, parent_widget, handler=None):
        self.widget = QWidget(parent_widget)
        # self.widget.setStyleSheet("border: 1px solid black; ")
        self.layout = QGridLayout(self.widget)
        self.children = []

        self.font = QtGui.QFont("Segoe UI")
        self.font.setPointSize(14)

    def configure(self, unique_values, max_plus_min):
        # clear layout
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().deleteLater()

        self.children = []
        for i, value in enumerate(unique_values):
            label_left = QtWidgets.QLabel(self.widget)
            label_left.setText(str(value))
            label_left.setFont(self.font)
            label_left.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            label_center = QtWidgets.QLabel(self.widget)
            icon = qta.icon("mdi.arrow-right", color="black")
            label_center.setPixmap(icon.pixmap(32, 32))
            label_center.setFixedWidth(32)

            label_right = QtWidgets.QLabel(self.widget)
            label_right.setText(str(max_plus_min - value))
            label_right.setFont(self.font)
            label_right.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            self.children.append(label_left)
            self.children.append(label_center)
            self.children.append(label_right)

            self.layout.addWidget(label_left, i, 0)
            self.layout.addWidget(label_center, i, 1)
            self.layout.addWidget(label_right, i, 2)



class ColumnSelector:
    def __init__(self, parent_widget):
        self.widget = CheckListWidget(parent_widget)
        self.widget.setFixedWidth(380)
        self.widget.setMinimumHeight(100)
        # self.widget.setGeometry(QtCore.QRect(10, 100, 381, 400))
        self.widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

    def configure(self, columns, selected_columns, allowed_columns):
        while self.widget.count() > 0:
            self.widget.takeItem(0)

        for column in columns:
            item = QListWidgetItem(column)
            self.widget.add_item_custom(item, checkable=column in allowed_columns, checked=column in selected_columns)
        self.widget.clearSelection()

    def get_selected_columns(self):
        return [
            self.widget.item(i).text()
            for i in range(self.widget.count())
            if self.widget.item(i).checkState() == Qt.Checked
        ]
