import qtawesome as qta
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QComboBox, QGridLayout, QHBoxLayout, QLabel, QListWidgetItem, QWidget

from src.common.constant import COLORS
from src.common.size import Font, SettingsPanelSize
from src.common.subclassed_widgets import CheckListWidget
from src.common.ui_constructor import create_label, create_label_editable_wordwrap, create_tool_button_qta
from src.common.unique_qss import set_stylesheet


class Title:
    def __init__(self, parent_widget, label_text):
        self.widget = create_label(
            parent=parent_widget,
            label_geometry=None,
            font_size=Font.size_small,
            alignment=QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter,
        )
        self.widget.setText(label_text)


class ColumnTypeSelector:
    def __init__(self, parent_widget, handler=None):
        self.widget = QComboBox(parent_widget)
        self.widget.addItem("None")
        self.widget.addItem("Nominal")
        self.widget.addItem("Ordinal")
        self.widget.addItem("Numerical")


class EditableTitleWordWrap:
    def __init__(self, parent_widget, label_text, handler=None):
        self.widget = create_label_editable_wordwrap(
            parent=parent_widget,
            font_size=Font.size_big,
            alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter,
        )
        # use only the needed vertical size

        self.widget.setText(label_text)
        if handler is not None:
            self.widget.editingFinished.connect(handler)


class BigAssCheckbox:
    def __init__(self, parent_widget, label_text, handler=None):
        self.widget = QCheckBox(parent_widget)
        set_stylesheet(
            self.widget,
            "#id{" "    font-family: 'Segoe UI';" f"   font-size: {Font.size}pt;" "}" "#id::indicator {"
            # "    margin-top: 2px;"
            f"    width: 20px;"
            f"    height: 20px;"
            "}"
            "#id::indicator:checked {"
            "    image: url(:/mat/resources/checked.png);"
            "}"
            "#id::indicator:unchecked {"
            "    image: url(:/mat/resources/unchecked.png);"
            "}"
            "#id::indicator:checked:disabled {"
            "    image: url(:/mat/resources/checked_disabled.png);"
            "}"
            "#id::indicator:unchecked:disabled {"
            "    image: url(:/mat/resources/unchecked_disabled.png);"
            "}",
        )
        self.widget.setText(label_text)
        if handler is not None:
            self.widget.stateChanged.connect(handler)


class BigAssButton:
    def __init__(self, parent_widget, label_text, icon_path, handler=None):
        self.widget = QWidget(parent_widget)
        self._margin = 20
        self._height = 81
        self.widget.setFixedHeight(self._height + self._margin)
        icon_path = icon_path if icon_path is not None else "msc.blank"

        self.button = create_tool_button_qta(
            parent=self.widget,
            button_geometry=QtCore.QRect(self._margin, self._margin, self._height, self._height),
            icon_path=icon_path,
            icon_size=QtCore.QSize(60, 60),
        )
        self.label = create_label(
            parent=self.widget,
            label_geometry=QtCore.QRect(120, self._margin, SettingsPanelSize.width - 120, self._height),
            font_size=Font.size_big,
            alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter,
        )
        self.label.setText(label_text)

        if handler is not None:
            self.button.clicked.connect(handler)
        else:
            self.widget.setEnabled(False)
        # self.button.pressed.connect(lambda: self.button.setDown(False))


class MediumAssButtonContainer:
    def __init__(self, parent_widget, widgets):
        self.widget = QWidget(parent_widget)
        self.layout = QGridLayout(self.widget)
        self.layout.setContentsMargins(20, 0, 20, 0)
        self.layout.setSpacing(10)
        self.widget.setLayout(self.layout)
        self.widgets = widgets
        for i, widget in enumerate(self.widgets.values()):
            self.layout.addWidget(widget.widget, i // 2, i % 2)


class MediumAssButton:
    def __init__(self, parent_widget, label_text, icon_path, handler=None):
        self.widget = QWidget(parent_widget)
        # self.widget.setStyleSheet("border: 1px solid black; ")
        self._margin_left = 0
        self._margin = 0
        self._height = 41
        self.widget.setFixedHeight(self._height + self._margin)
        self.widget.setFixedWidth(140)
        icon_path = icon_path if icon_path is not None else "msc.blank"

        self.button = create_tool_button_qta(
            parent=self.widget,
            button_geometry=QtCore.QRect(self._margin_left, self._margin, self._height, self._height),
            icon_path=icon_path,
            icon_size=QtCore.QSize(35, 35),
        )
        self.label = create_label(
            parent=self.widget,
            label_geometry=QtCore.QRect(50, self._margin, 80, self._height),
            font_size=Font.size,
            alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter,
        )
        self.label.setText(label_text)

        if handler is not None:
            self.button.clicked.connect(handler)
        else:
            self.widget.setEnabled(False)
        self.button.clicked.connect(lambda: self.button.setDown(False))


class Spacer:
    def __init__(self, parent_widget):
        self.widget = QWidget(parent_widget)
        self.widget.setFixedHeight(40)


class SpacerSmall:
    def __init__(self, parent_widget):
        self.widget = QWidget(parent_widget)
        self.widget.setFixedHeight(8)


class ColumnColorSelector:
    def __init__(self, parent_widget, handler=None):
        self.widget = QWidget(parent_widget)
        self.layout = QGridLayout(self.widget)

        self.buttons = []

        def get_handler(index):
            return lambda: handler(index)

        for i, color in enumerate(COLORS):
            button = QtWidgets.QToolButton(self.widget)
            button.setFixedWidth(35)
            button.setFixedHeight(35)
            button.setText("")
            set_stylesheet(button, "#id{" + f"background-color: {color}" + "}")
            button.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly)
            self.buttons.append(button)
            self.layout.addWidget(button, i // 6, i % 6)
            button.clicked.connect(get_handler(i))


class InvertVisualizer:
    def __init__(self, parent_widget, handler=None):
        self.widget = QWidget(parent_widget)
        # self.widget.setStyleSheet("border: 1px solid black; ")
        self.layout = QGridLayout(self.widget)
        self.children = []

        self.font = QtGui.QFont("Segoe UI")
        self.font.setPointSize(Font.size)

    def configure(self, unique_values, max_plus_min):
        # clear layout
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().deleteLater()

        self.children = []
        for i, value in enumerate(unique_values):
            label_left = QtWidgets.QLabel(self.widget)
            label_left.setText(str(value))
            label_left.setFont(self.font)
            label_left.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            label_center = QtWidgets.QLabel(self.widget)
            icon = qta.icon("mdi.arrow-right", color="black")
            label_center.setPixmap(icon.pixmap(32, 32))
            label_center.setFixedWidth(32)

            label_right = QtWidgets.QLabel(self.widget)
            label_right.setText(str(max_plus_min - value))
            label_right.setFont(self.font)
            label_right.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            self.children.append(label_left)
            self.children.append(label_center)
            self.children.append(label_right)

            self.layout.addWidget(label_left, i, 0)
            self.layout.addWidget(label_center, i, 1)
            self.layout.addWidget(label_right, i, 2)


class ColumnSelector:
    def __init__(self, parent_widget):
        self.widget = CheckListWidget(parent_widget)

        self.widget.setFixedWidth(SettingsPanelSize.width - 15)
        self.widget.setMinimumHeight(100)
        # self.widget.setGeometry(QtCore.QRect(10, 100, 381, 400))
        self.widget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.items = []

    def configure(self, columns, selected_columns, allowed_columns):
        while self.widget.count() > 0:
            self.widget.takeItem(0)
        self.items = []
        for column in columns:
            item = QListWidgetItem()
            item.setFont(QtGui.QFont("Segoe UI", Font.size))

            widget = QWidget()
            label = QLabel(column)
            set_stylesheet(label, f"font-size: {Font.size}pt;" 'font-family: "Segoe UI";' "margin-left: 10px;")
            # Layout to hold the label
            layout = QHBoxLayout()
            layout.addWidget(label)
            layout.addStretch()  # Add stretch to push text to the left
            layout.setContentsMargins(0, 0, 0, 0)  # Add some padding around the text

            # Set the layout on the QWidget
            widget.setLayout(layout)

            self.widget.add_item_custom(
                item, checkable=column in allowed_columns, checked=column in selected_columns, widget=widget
            )
            self.items.append(column)

        self.widget.clearSelection()

    def get_selected_columns(self):
        return [
            self.items[i] for i in range(len(self.items)) if self.widget.item(i).checkState() == Qt.CheckState.Checked
        ]
