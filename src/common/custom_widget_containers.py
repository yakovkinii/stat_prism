import logging
from typing import Callable, List

import attrs
import qtawesome as qta
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

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


class ColumnFilter:
    def __init__(self, parent_widget, on_change_handler):
        """
        This widget will be used to filter the values.
        It will be 2 drop-downs: for col name and for type of filter.
        the 3rd one will be the selector: some formula or something
        """
        self.widget = QWidget(parent_widget)
        self.layout = QGridLayout(self.widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.widget.setLayout(self.layout)

        self.filter_value = QLineEdit(self.widget)
        self.filter_value.setFixedWidth(100)
        self.filter_value.textChanged.connect(on_change_handler)
        self.layout.addWidget(self.filter_value)


def empty_widget(
    parent,
    inner_layout_class=None,
    widget_class=None,
    outer_layout=None,
    setup: Callable[[object, object], any] = None,
):
    if inner_layout_class is None:
        inner_layout_class = QVBoxLayout
    if widget_class is None:
        widget_class = QWidget

    widget = widget_class(parent)
    layout = inner_layout_class(widget)
    widget.setLayout(layout)

    if outer_layout is not None:
        outer_layout.addWidget(widget)

    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    if setup is not None:
        _ = setup(widget, layout)

    return widget, layout


def widget_in_layout(
    widget,
    layout,
    setup: Callable[[object, object], any] = None,
):
    layout.addWidget(widget)
    if setup is not None:
        _ = setup(widget, layout)
    return widget


def clean_up_list_widget(list_widget):
    for index in range(list_widget.count()):
        item = list_widget.item(index)
        widget = list_widget.itemWidget(item)
        if widget:
            widget.deleteLater()
        list_widget.takeItem(index)
    list_widget.clear()


class QWidgetClickable(QFrame):
    clicked = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class QListWidgetClickable(QtWidgets.QListWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.reasonable_number_of_columns = 6
        self.height = 18

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.parent().mousePressEvent(event)

    def sizeHint(self):
        logging.info(f"Size hint called")
        return QtCore.QSize(20, self.calculate_height())

    def minimumSizeHint(self):
        return self.sizeHint()

    def calculate_height(self):
        new_height = self.height * self.reasonable_number_of_columns + 6
        # If horizontal scrollbar is visible, add its height
        if self.horizontalScrollBar().isVisible():
            hrheight = self.horizontalScrollBar().height()
        else:
            hrheight = 0
        logging.info(f"Horizontal scrollbar height: {hrheight}")
        return new_height + hrheight


@attrs.define
class Column:
    name: str
    column_dtype: str


@attrs.define
class Field:
    name: str
    allowed_column_dtypes: List[str]
    reasonable_number_of_columns: int = 5
    allow_only_single_column: bool = False


class ColumnSelectorEx:
    def __init__(
        self, parent_widget, fields: List[Field], clicked_handler: Callable, study_settings_changed_handler: Callable
    ):
        self.fields = fields
        self.allowed_columns = None
        self.columns = None
        self.study_settings_changed_handler = study_settings_changed_handler
        self.clicked_handler = clicked_handler

        self.popup = ColumnSelectorExPopup(parent_widget, fields)
        self.popup.widget.hide()

        self.widget, self.layout = empty_widget(
            parent=parent_widget,
            inner_layout_class=QVBoxLayout,
            widget_class=QWidgetClickable,
            setup=lambda widget, layout: [
                widget.clicked.connect(self.clicked_handler),
            ],
        )

        self.fields_panel, self.fields_panel_layout = empty_widget(
            parent=self.widget,
            inner_layout_class=QVBoxLayout,
            outer_layout=self.layout,
        )

        self.panel_list_widgets = []
        for index, field in enumerate(fields):
            panel, panel_layout = empty_widget(
                parent=self.fields_panel,
                inner_layout_class=QVBoxLayout,
                outer_layout=self.fields_panel_layout,
            )
            _ = widget_in_layout(
                widget=QLabel(panel),
                layout=panel_layout,
                setup=lambda widget, layout: [
                    widget.setText(field.name),
                ],
            )

            panel_list = widget_in_layout(
                widget=QListWidgetClickable(panel),
                layout=panel_layout,
                setup=lambda widget, layout: (
                    widget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection),
                    widget.setFocusPolicy(Qt.FocusPolicy.NoFocus),
                ),
            )
            self.panel_list_widgets.append(panel_list)

    def configure(self, columns, selected_columns_list, allowed_columns):
        self.columns = columns
        self.allowed_columns = allowed_columns
        for panel_list, selected_columns in zip(self.panel_list_widgets, selected_columns_list):
            clean_up_list_widget(panel_list)
            panel_list.addItems(selected_columns)

    def configure_popup(self):
        selected_columns_list = [
            [list_widget.item(i).text() for i in range(list_widget.count())] for list_widget in self.panel_list_widgets
        ]
        self.popup.configure(
            columns=self.columns,
            selected_columns_list=selected_columns_list,
            allowed_columns=self.allowed_columns,
        )

    def configure_from_popup(self):
        logging.info("Popup closed")
        if not self.popup.success:
            return
        for panel_list, popup_panel_list in zip(self.panel_list_widgets, self.popup.panel_list_widgets):
            clean_up_list_widget(panel_list)
            items = [popup_panel_list.item(i).text() for i in range(popup_panel_list.count())]
            panel_list.addItems(items)
            logging.info(f"Adding {items} to panel list")
            # tell layout to recalculate heights
            panel_list.updateGeometry()

        self.study_settings_changed_handler()

    def get_selected_columns(self):
        return [
            [list_widget.item(i).text() for i in range(list_widget.count())] for list_widget in self.panel_list_widgets
        ]


class ColumnSelectorExPopup:
    def __init__(self, parent_widget, fields: List[Field]):
        self.success = False
        self.widget, self.layout = empty_widget(
            parent=parent_widget,
            inner_layout_class=QVBoxLayout,
            widget_class=QDialog,
            setup=lambda widget, layout: [layout.setContentsMargins(0, 5, 0, 5), layout.setSpacing(10)],
        )
        self.main_list = widget_in_layout(
            widget=QListWidget(self.widget),
            layout=self.layout,
            setup=lambda widget, layout: [
                widget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection),
                widget.clicked.connect(self.main_list_clicked),
                widget.setFocusPolicy(Qt.FocusPolicy.NoFocus),
            ],
        )
        self.fields_panel, self.fields_panel_layout = empty_widget(
            parent=self.widget,
            inner_layout_class=QVBoxLayout,
            outer_layout=self.layout,
        )

        self.panel_list_widgets = []
        self.panel_list_buttons = []
        for index, field in enumerate(fields):
            panel, panel_layout = empty_widget(
                parent=self.fields_panel,
                inner_layout_class=QVBoxLayout,
                outer_layout=self.fields_panel_layout,
            )
            _ = widget_in_layout(
                widget=QLabel(panel),
                layout=panel_layout,
                setup=lambda widget, layout: widget.setText(field.name),
            )
            button_list, button_list_layout = empty_widget(
                parent=panel,
                inner_layout_class=QHBoxLayout,
                outer_layout=panel_layout,
                setup=lambda widget, layout: (layout.setSpacing(5),),
            )
            button_stretch, button_stretch_layout = empty_widget(
                parent=button_list,
                inner_layout_class=QVBoxLayout,
                outer_layout=button_list_layout,
            )

            panel_list_button = widget_in_layout(
                widget=create_tool_button_qta(
                    parent=button_stretch,
                    button_geometry=None,
                    icon_path="ph.arrow-bend-down-right",
                    icon_size=QtCore.QSize(25, 25),
                ),
                layout=button_stretch_layout,
                setup=lambda widget, layout: [
                    widget.setText("Add"),
                    widget.clicked.connect((lambda _: lambda: self.button_pressed(_))(index)),
                ],
            )
            button_stretch_layout.addStretch()

            panel_list = widget_in_layout(
                widget=QListWidget(button_list),
                layout=button_list_layout,
                setup=lambda widget, layout: (
                    widget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection),
                    widget.clicked.connect((lambda _: lambda: self.panel_list_clicked(_))(index)),
                    widget.setFocusPolicy(Qt.FocusPolicy.NoFocus),
                ),
            )
            self.panel_list_widgets.append(panel_list)
            self.panel_list_buttons.append(panel_list_button)

    def configure(self, columns, selected_columns_list, allowed_columns):
        clean_up_list_widget(self.main_list)
        self.main_list.addItems(columns)
        for panel_list, selected_columns in zip(self.panel_list_widgets, selected_columns_list):
            clean_up_list_widget(panel_list)
            panel_list.addItems(selected_columns)
        self.success = False

    def main_list_clicked(self):
        logging.info("Main list clicked")
        for button in self.panel_list_buttons:
            button.setIcon(qta.icon("ph.arrow-bend-down-right"))
            button.setText("Add")
            button.setEnabled(True)

    def panel_list_clicked(self, panel_index):
        logging.info(f"Panel {panel_index} clicked")
        for button_index, button in enumerate(self.panel_list_buttons):
            if button_index == panel_index:
                button.setIcon(qta.icon("ph.arrow-bend-left-up"))
                button.setText("Remove")
                button.setEnabled(True)
            else:
                button.setIcon(qta.icon("ph.arrow-bend-left-up"))
                button.setText("Remove")
                button.setEnabled(False)

    def button_pressed(self, button_index):
        logging.info(f"Button {button_index} pressed")
        button = self.panel_list_buttons[button_index]
        panel_list = self.panel_list_widgets[button_index]
        if button.text() == "Add":
            selected_main = self.main_list.currentItem()
            if selected_main is not None:
                panel_list.addItem(selected_main.text())
                self.main_list.takeItem(self.main_list.currentRow())
        elif button.text() == "Remove":
            selected_list1 = panel_list.currentItem()
            if selected_list1 is not None:
                self.main_list.addItem(selected_list1.text())
                panel_list.takeItem(panel_list.currentRow())


class ColumnSelectorPopupHolder:
    def __init__(self, parent_widget):
        self.popup = None
        self.widget, self.layout = empty_widget(
            parent=parent_widget,
            inner_layout_class=QVBoxLayout,
            widget_class=QWidget,
        )

    def configure(self, popup: ColumnSelectorExPopup):
        if self.popup is not None:
            self.layout.removeWidget(self.popup.widget)
            self.popup.widget.hide()

        self.popup = popup
        self.layout.addWidget(self.popup.widget)
        self.popup.widget.show()
