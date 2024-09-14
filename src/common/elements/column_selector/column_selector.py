import logging
from typing import List

import attrs
import qtawesome as qta
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QListWidgetItem, QVBoxLayout, QWidget

from src.common.constant import COLUMN_TYPE_ICONS, ColumnType
from src.common.elements.base.base import BasePanelElement
from src.common.elements.utility.layout_helpers import clean_up_list_widget, empty_widget, widget_in_layout
from src.common.elements.utility.primitive_elements import QListWidgetClickable, QWidgetClickable
from src.common.messages import Message, MessageType
from src.common.size import Font
from src.common.ui_constructor import create_tool_button_qta
from src.common.unique_qss import set_stylesheet


@attrs.define
class Column:
    name: str
    column_type: ColumnType


@attrs.define
class Field:
    name: str
    column_type: ColumnType
    reasonable_number_of_columns: int = 5
    allow_only_single_column: bool = False


class ColumnSelectorEx(BasePanelElement):
    def __init__(self, fields: List[Field]):
        super().__init__()
        self.layout = None
        self.popup = None
        self.fields_panel_layout = None
        self.fields_panel = None
        self.fields = fields
        self.columns = None
        self.panel_list_widgets = []

    def setup(self):
        self.popup = ColumnSelectorExPopup(self.parent_widget, self.fields)
        self.popup.widget.hide()

        self.widget, self.layout = empty_widget(
            parent=self.parent_widget,
            inner_layout_class=QVBoxLayout,
            widget_class=QWidgetClickable,
            setup=lambda widget, layout: [
                widget.clicked.connect(
                    lambda: self.handler(
                        Message(
                            message_type=MessageType.CLICKED,
                            payload=None,
                            caller_id=self.element_id,
                        )
                    )
                ),
            ],
        )

        self.fields_panel, self.fields_panel_layout = empty_widget(
            parent=self.widget,
            inner_layout_class=QVBoxLayout,
            outer_layout=self.layout,
            setup=lambda widget, layout: [
                layout.setContentsMargins(2, 2, 2, 2),
                layout.setSpacing(15),
            ],
        )

        for index, field in enumerate(self.fields):
            panel, panel_layout = empty_widget(
                parent=self.fields_panel,
                inner_layout_class=QVBoxLayout,
                outer_layout=self.fields_panel_layout,
            )

            title, title_layout = empty_widget(
                parent=panel,
                inner_layout_class=QHBoxLayout,
                outer_layout=panel_layout,
            )

            _ = widget_in_layout(
                widget=QLabel(title),
                layout=title_layout,
                setup=lambda widget, layout: [
                    widget.setText(field.name),
                    set_stylesheet(widget, f"font-size: {Font.size_big}px;"),
                ],
            )
            title_layout.addStretch()

            panel_list = widget_in_layout(
                widget=QListWidgetClickable(panel),
                layout=panel_layout,
                setup=lambda widget, layout: (
                    widget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection),
                    widget.setFocusPolicy(Qt.FocusPolicy.NoFocus),
                    set_stylesheet(widget, "#id{border: 1px solid #ddd;}"),
                ),
            )
            panel_list.reasonable_number_of_columns = field.reasonable_number_of_columns

            self.panel_list_widgets.append(panel_list)

    def configure(self, columns: List[Column], selected_columns_list):
        self.columns = columns
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

        self.handler(
            Message(
                message_type=MessageType.STATE_CHANGED,
                payload=None,
                caller_id=self.element_id,
            )
        )

    def get_selected_columns(self):
        return [
            [list_widget.item(i).text() for i in range(list_widget.count())] for list_widget in self.panel_list_widgets
        ]


class ColumnSelectorExPopup:
    def __init__(self, parent_widget, fields: List[Field]):
        self.allow_ok_button_handler = None
        self.fields = fields
        self.columns: List[Column] = []
        self.column_names: List[str] = []
        self.success = False
        self.widget, self.layout = empty_widget(
            parent=parent_widget,
            inner_layout_class=QVBoxLayout,
            widget_class=QDialog,
            setup=lambda widget, layout: [layout.setContentsMargins(0, 5, 0, 5), layout.setSpacing(10)],
        )
        self.main_list = widget_in_layout(
            widget=QListWidgetClickable(self.widget),
            layout=self.layout,
            setup=lambda widget, layout: [
                widget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection),
                widget.clicked.connect(self.main_list_clicked),
                widget.selectionModel().selectionChanged.connect(self.main_list_clicked),
                widget.setFocusPolicy(Qt.FocusPolicy.NoFocus),
                widget.setDragEnabled(True),
                widget.setAcceptDrops(True),
                widget.setDropIndicatorShown(True),
                widget.setDefaultDropAction(QtCore.Qt.MoveAction),
                set_stylesheet(widget, "#id{border: 1px solid #ddd;}"),
            ],
        )
        self.main_list.reasonable_number_of_columns = 16

        self.fields_panel, self.fields_panel_layout = empty_widget(
            parent=self.widget,
            inner_layout_class=QVBoxLayout,
            outer_layout=self.layout,
            setup=lambda widget, layout: [
                layout.setContentsMargins(2, 2, 2, 2),
                layout.setSpacing(15),
            ],
        )

        self.panel_list_widgets = []
        self.panel_list_buttons = []
        self.panel_list_icons = []
        for index, field in enumerate(fields):
            panel, panel_layout = empty_widget(
                parent=self.fields_panel,
                inner_layout_class=QVBoxLayout,
                outer_layout=self.fields_panel_layout,
            )

            title, title_layout = empty_widget(
                parent=panel,
                inner_layout_class=QHBoxLayout,
                outer_layout=panel_layout,
            )

            _ = widget_in_layout(
                widget=QLabel(title),
                layout=title_layout,
                setup=lambda widget, layout: [
                    widget.setText(field.name),
                    set_stylesheet(widget, f"font-size: {Font.size_big}px;"),
                ],
            )
            title_layout.addStretch()
            icon = widget_in_layout(
                widget=QLabel(title),
                layout=title_layout,
                setup=lambda widget, layout: [
                    set_stylesheet(widget, f"font-size: {Font.size_big}px;"),
                    widget.setPixmap(COLUMN_TYPE_ICONS[field.column_type].pixmap(24, 24)),
                ],
            )
            self.panel_list_icons.append(icon)

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

            list_stretch, list_stretch_layout = empty_widget(
                parent=button_list,
                inner_layout_class=QVBoxLayout,
                outer_layout=button_list_layout,
            )

            panel_list = widget_in_layout(
                widget=QListWidgetClickable(list_stretch),
                layout=list_stretch_layout,
                setup=lambda widget, layout: (
                    widget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection),
                    widget.clicked.connect((lambda _: lambda: self.panel_list_clicked(_))(index)),
                    widget.selectionModel().selectionChanged.connect(
                        (lambda _: lambda: self.panel_list_clicked(_))(index)
                    ),
                    widget.setFocusPolicy(Qt.FocusPolicy.NoFocus),
                    widget.setDragEnabled(True),
                    widget.setAcceptDrops(True),
                    widget.setDropIndicatorShown(True),
                    widget.setDefaultDropAction(QtCore.Qt.MoveAction),
                    layout.setContentsMargins(0, 0, 0, 0),
                    set_stylesheet(widget, "#id{border: 1px solid #ddd;}"),
                ),
            )
            panel_list.reasonable_number_of_columns = field.reasonable_number_of_columns
            list_stretch_layout.addStretch()

            self.panel_list_widgets.append(panel_list)
            self.panel_list_buttons.append(panel_list_button)

            panel_list.dropEvent = lambda event, _=index: self.dropEvent(event, index)
        self.main_list.dropEvent = lambda event: self.dropEvent(event, -1)

    def configure(self, columns: List[Column], selected_columns_list: List[List[str]]):
        clean_up_list_widget(self.main_list)
        self.columns = columns
        self.column_names = [column.name for column in columns]
        main_list_names = [column.name for column in columns]

        for panel_list, selected_columns in zip(self.panel_list_widgets, selected_columns_list):
            clean_up_list_widget(panel_list)
            for column in selected_columns:
                main_list_names.remove(column)
                item = QListWidgetItem(column)
                item.setIcon(COLUMN_TYPE_ICONS[columns[self.column_names.index(column)].column_type])
                panel_list.addItem(item)
            # panel_list.addItems(selected_columns)

        for column in main_list_names:
            item = QListWidgetItem(column)
            item.setIcon(COLUMN_TYPE_ICONS[columns[self.column_names.index(column)].column_type])
            self.main_list.addItem(item)
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

    def dropEvent(self, event, index):
        source_list = event.source()
        target_list = self.panel_list_widgets[index] if index != -1 else self.main_list
        if target_list == source_list:
            super(QListWidgetClickable, source_list).dropEvent(event)
            self.allow_ok_button_handler()
            event.ignore()
            return

        if isinstance(target_list, QListWidgetClickable):
            if source_list == self.main_list:
                self.button_pressed(index, from_drop=True, remove=False)
            else:
                self.button_pressed(index, from_drop=True, remove=True)
        event.ignore()

    def button_pressed(self, button_index, from_drop=False, remove=False):
        logging.info(f"Button {button_index} pressed")
        button = self.panel_list_buttons[button_index]
        panel_list = self.panel_list_widgets[button_index]
        if (button.text() == "Add" and not from_drop) or (from_drop and not remove):
            selected_main = self.main_list.selectedItems() if not from_drop else [self.main_list.currentItem()]
            if selected_main:
                selected_main_names = [item.text() for item in selected_main]
                selected_main_types = [
                    self.columns[self.column_names.index(item)].column_type for item in selected_main_names
                ]
                panel_type = self.fields[button_index].column_type
                if not all([selected_main_type == panel_type for selected_main_type in selected_main_types]):
                    icon = self.panel_list_icons[button_index]
                    old_pixmap = icon.pixmap()
                    icon.setPixmap(qta.icon("mdi.alert", color="red").pixmap(24, 24))
                    QtCore.QTimer.singleShot(50, lambda _=old_pixmap: icon.setPixmap(_))
                    return

                for item in selected_main:
                    new_item = QListWidgetItem(item.text())
                    new_item.setIcon(item.icon())
                    panel_list.addItem(new_item)
                    self.main_list.takeItem(self.main_list.row(item))
                if self.allow_ok_button_handler is not None:
                    self.allow_ok_button_handler()
        elif (button.text() == "Remove" and not from_drop) or (from_drop and remove):
            selected_list = panel_list.selectedItems() if not remove else [panel_list.currentItem()]
            if selected_list:
                for item in selected_list:
                    new_item = QListWidgetItem(item.text())
                    new_item.setIcon(item.icon())
                    self.main_list.addItem(new_item)
                    panel_list.takeItem(panel_list.row(item))

                sorted_items = sorted(
                    (self.main_list.item(i).text() for i in range(self.main_list.count())),
                    key=lambda x: self.column_names.index(x),
                )
                clean_up_list_widget(self.main_list)
                for item in sorted_items:
                    new_item = QListWidgetItem(item)
                    new_item.setIcon(COLUMN_TYPE_ICONS[self.columns[self.column_names.index(item)].column_type])
                    self.main_list.addItem(new_item)
                if self.allow_ok_button_handler is not None:
                    self.allow_ok_button_handler()


class ColumnSelectorPopupHolder(BasePanelElement):
    def __init__(self):
        super().__init__()
        self.layout = None
        self.popup = None

    def setup(self):
        self.widget, self.layout = empty_widget(
            parent=self.parent_widget,
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
