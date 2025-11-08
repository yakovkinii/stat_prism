#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from typing import List

import attrs
import qtawesome as qta
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidgetItem,
    QVBoxLayout,
)

from src.common.constant import COLUMN_TYPE_ICONS, ColumnType, SettingsPanelSize
from src.common.decorators import log_method, log_method_noarg
from src.common.ui_constructor import create_tool_button_qta
from src.data.data import DataColumn
from src.data.data_manager import DATA_MANAGER
from src.pyside_ext.elements.utility.layout_helpers import (
    add_widget,
    clean_up_list_widget,
    widget_in_layout,
)
from src.pyside_ext.elements.utility.primitive_elements import (
    QListWidgetClickable,
    QWidgetClickable,
)
from src.pyside_ext.layout import GridLayout, HBoxLayout, VBoxLayout
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfig

ITEM_HEIGHT = 20


@attrs.define
class Field:
    name: str
    column_type: ColumnType
    reasonable_number_of_columns: int = 5
    allow_only_single_column: bool = False
    minimum_columns: int = 0


class IISPWACColumnSelector(ItemInSidePanelWithAutoConfig):
    def __init__(self, fields: List[Field]):
        super().__init__()
        self.fields = fields
        self.handler_changed = None

    def post_init(self, name, parent_widget):
        self.popup = ColumnSelectorExPopup(None, self.fields, handler_popup_close=self.popup_closed)
        self.popup.widget.hide()

        self.name = name
        self.widget, self.layout = add_widget(
            parent=parent_widget,
            inner_layout_class=VBoxLayout,
            widget_class=QWidgetClickable,
            css=css(border=Style.General.border_elevated),
        )
        self.widget.clicked.connect(self.handler_open_popup)

        self.fields_panel, self.fields_panel_layout = add_widget(
            parent=self.widget,
            inner_layout_class=VBoxLayout,
            outer_layout=self.layout,
        )
        self.fields_panel_layout.setContentsMargins(2, 2, 2, 2)
        self.fields_panel_layout.setSpacing(15)

        self.panel_list_widgets = []
        self.panel_list_buttons = []
        self.panel_list_icons = []
        for index, field in enumerate(self.fields):
            panel, panel_layout = add_widget(
                parent=self.fields_panel,
                inner_layout_class=VBoxLayout,
                outer_layout=self.fields_panel_layout,
                css=css(border="solid 1px blue"),
            )

            title, title_layout = add_widget(
                parent=panel,
                inner_layout_class=HBoxLayout,
                outer_layout=panel_layout,
            )

            field_label, _ = add_widget(
                widget=QLabel(title),
                outer_layout=title_layout,
                css=css(
                    font_size=Style.FontSize.regular,
                ),
            )
            field_label.setText(field.name)

            title_layout.addStretch()

            pixmaps = [COLUMN_TYPE_ICONS[field.column_type].pixmap(24, 24)]
            if field.column_type == ColumnType.ORDINAL:
                pixmaps.append(COLUMN_TYPE_ICONS[ColumnType.NUMERIC].pixmap(24, 24))
            elif field.column_type == ColumnType.NOMINAL:
                pixmaps.append(COLUMN_TYPE_ICONS[ColumnType.ORDINAL].pixmap(24, 24))
                pixmaps.append(COLUMN_TYPE_ICONS[ColumnType.NUMERIC].pixmap(24, 24))

            for pixmap in pixmaps:
                icon = widget_in_layout(
                    widget=QLabel(title),
                    layout=title_layout,
                    setup=lambda widget, layout: [
                        widget.setPixmap(pixmap),
                    ],
                )
                self.panel_list_icons.append(icon)

            panel_list, panel_list_layout = add_widget(
                parent=panel,
                widget_class=QListWidgetClickable,
                outer_layout=panel_layout,
                css=css(
                    border=Style.General.border,
                    border_color=Style.Color.BorderElevated,
                ),
            )
            panel_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection),
            panel_list.clicked.connect(self.handler_open_popup)
            panel_list.setFocusPolicy(Qt.FocusPolicy.NoFocus),
            panel_list.setDragEnabled(True),
            panel_list.setAcceptDrops(True),
            panel_list.setDropIndicatorShown(True),
            panel_list.setDefaultDropAction(QtCore.Qt.DropAction.MoveAction),
            panel_list.reasonable_number_of_columns = field.reasonable_number_of_columns

            self.panel_list_widgets.append(panel_list)

        self.clear_alert()

    @log_method
    def set_alert(self, field_index: int):
        set_stylesheet(self.panel_list_widgets[field_index], css(border="1px solid red"))

    @log_method_noarg
    def clear_alert(self):
        for i in range(len(self.panel_list_widgets)):
            set_stylesheet(self.panel_list_widgets[i], css(border=Style.General.border_elevated))

    def configure(self, **kwargs):
        assert "data_source" in kwargs, "data_source element must be present to configure Column Selector."
        data_label = kwargs["data_source"]
        if data_label is None:
            data_label = "Auto"
        result_id = kwargs["result_id"]

        selected_columns_list = kwargs[self.name]
        if selected_columns_list is None:
            selected_columns_list = [[] for _ in self.fields]
        selected_columns_list = selected_columns_list.copy()

        columns: List[DataColumn] = DATA_MANAGER.get_data_from_data_label(
            data_label=data_label,
            current_result_id=result_id,
        ).get_all_columns_as_column_types()

        self.columns = columns
        self.selected_columns_list = selected_columns_list

        self.columns = columns
        self.column_names = [column.column_name for column in columns]
        main_list_names = [column.column_name for column in columns]

        for panel_list, selected_columns in zip(self.panel_list_widgets, selected_columns_list):
            clean_up_list_widget(panel_list)
            for column in selected_columns:
                if column not in main_list_names:
                    continue
                main_list_names.remove(column)
                item = QListWidgetItem(column)
                item.setIcon(COLUMN_TYPE_ICONS[columns[self.column_names.index(column)].column_type])
                item.setSizeHint(QtCore.QSize(0, ITEM_HEIGHT))
                panel_list.addItem(item)

    @log_method_noarg
    def handler_open_popup(self):
        self.popup.configure(self.columns, self.selected_columns_list)
        self.popup.widget.show()

    @log_method_noarg
    def popup_closed(self):
        for i, (panel_list, popup_panel_list) in enumerate(zip(self.panel_list_widgets, self.popup.panel_list_widgets)):
            clean_up_list_widget(panel_list)
            selected_columns = [popup_panel_list.item(i).text() for i in range(popup_panel_list.count())]
            self.selected_columns_list[i] = selected_columns
            for column in selected_columns:
                item = QListWidgetItem(column)
                item.setIcon(COLUMN_TYPE_ICONS[self.columns[self.column_names.index(column)].column_type])
                item.setSizeHint(QtCore.QSize(0, ITEM_HEIGHT))
                panel_list.addItem(item)
            # tell layout to recalculate heights
            panel_list.updateGeometry()

        if self.handler_changed is not None:
            self.handler_changed()
        self.on_recalculate()

    def get_kwargs(self):
        return {self.name: self.selected_columns_list.copy()}

    def set_handler_changed(self, handler: callable):
        self.handler_changed = handler


class ColumnSelectorExPopup:
    def __init__(self, parent_widget, fields: List[Field], handler_popup_close: callable):
        self.fields = fields
        self.columns: List[DataColumn] = []
        self.column_names: List[str] = []
        self.handler_popup_close = handler_popup_close
        self.success = False

        self.widget, self.layout = add_widget(
            parent=parent_widget,
            inner_layout_class=HBoxLayout,
            widget_class=QDialog,
        )
        self.widget.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.widget.setWindowTitle("Select Columns")
        self.widget.setMinimumWidth(SettingsPanelSize.popup_minimum_width)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        self.widget.closeEvent = lambda event: self.handler_close()
        # self.widget.dismissed.connect(self.handler_close)

        self.main_list, _ = add_widget(
            parent=self.widget,
            widget_class=QListWidgetClickable,
            outer_layout=self.layout,
            css=css(
                border=Style.General.border,
                border_color=Style.Color.BorderElevated,
            ),
        )
        self.main_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.main_list.clicked.connect(self.main_list_clicked)
        self.main_list.selectionModel().selectionChanged.connect(self.main_list_clicked)
        self.main_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.main_list.setDragEnabled(True)
        self.main_list.setAcceptDrops(True)
        self.main_list.setDropIndicatorShown(True)
        self.main_list.setDefaultDropAction(QtCore.Qt.DropAction.MoveAction)

        self.main_list.reasonable_number_of_columns = 16

        self.fields_panel, self.fields_panel_layout = add_widget(
            parent=self.widget,
            inner_layout_class=VBoxLayout,
            outer_layout=self.layout,
        )
        self.fields_panel_layout.setContentsMargins(2, 2, 2, 2)
        self.fields_panel_layout.setSpacing(15)

        self.panel_list_widgets = []
        self.panel_list_buttons = []
        self.panel_list_icons = []
        for index, field in enumerate(fields):
            panel, panel_layout = add_widget(
                parent=self.fields_panel,
                inner_layout_class=GridLayout,
                outer_layout=self.fields_panel_layout,
            )

            title, title_layout = add_widget(
                parent=panel,
                inner_layout_class=HBoxLayout,
                outer_layout=panel_layout,
                outer_layout_grid_column=1,
                outer_layout_grid_row=0,
            )

            field_label, _ = add_widget(
                widget=QLabel(title),
                outer_layout=title_layout,
                css=css(
                    font_size=Style.FontSize.regular,
                ),
            )
            field_label.setText(field.name)

            title_layout.addStretch()

            pixmaps = [COLUMN_TYPE_ICONS[field.column_type].pixmap(24, 24)]
            if field.column_type == ColumnType.ORDINAL:
                pixmaps.append(COLUMN_TYPE_ICONS[ColumnType.NUMERIC].pixmap(24, 24))
            elif field.column_type == ColumnType.NOMINAL:
                pixmaps.append(COLUMN_TYPE_ICONS[ColumnType.ORDINAL].pixmap(24, 24))
                pixmaps.append(COLUMN_TYPE_ICONS[ColumnType.NUMERIC].pixmap(24, 24))

            for pixmap in pixmaps:
                icon = widget_in_layout(
                    widget=QLabel(title),
                    layout=title_layout,
                    setup=lambda widget, layout: [
                        widget.setPixmap(pixmap),
                    ],
                )
                self.panel_list_icons.append(icon)

            button_stretch, button_stretch_layout = add_widget(
                parent=panel,
                inner_layout_class=VBoxLayout,
                outer_layout=panel_layout,
                outer_layout_grid_column=0,
                outer_layout_grid_row=1,
            )
            button_stretch_layout.setContentsMargins(0, 0, 5, 0)

            panel_list_button, _ = add_widget(
                widget=create_tool_button_qta(
                    parent=button_stretch,
                    button_geometry=None,
                    icon_path="ph.arrow-bend-down-right",
                    icon_size=QtCore.QSize(25, 25),
                ),
                outer_layout=button_stretch_layout,
            )
            panel_list_button.setText("Add")
            panel_list_button.clicked.connect((lambda _: lambda: self.button_pressed(_))(index))

            button_stretch_layout.addStretch()

            list_stretch, list_stretch_layout = add_widget(
                parent=panel,
                inner_layout_class=VBoxLayout,
                outer_layout=panel_layout,
                outer_layout_grid_column=1,
                outer_layout_grid_row=1,
            )

            panel_list, panel_list_layout = add_widget(
                widget=QListWidgetClickable(list_stretch),
                outer_layout=list_stretch_layout,
                css=css(
                    border=Style.General.border,
                    border_color=Style.Color.BorderElevated,
                ),
            )
            panel_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection),
            panel_list.clicked.connect((lambda _: lambda: self.panel_list_clicked(_))(index)),
            panel_list.selectionModel().selectionChanged.connect((lambda _: lambda: self.panel_list_clicked(_))(index)),
            panel_list.setFocusPolicy(Qt.FocusPolicy.NoFocus),
            panel_list.setDragEnabled(True),
            panel_list.setAcceptDrops(True),
            panel_list.setDropIndicatorShown(True),
            panel_list.setDefaultDropAction(QtCore.Qt.DropAction.MoveAction),
            # panel_list_layout.setContentsMargins(0, 0, 0, 0),
            panel_list.reasonable_number_of_columns = field.reasonable_number_of_columns
            list_stretch_layout.addStretch()

            self.panel_list_widgets.append(panel_list)
            self.panel_list_buttons.append(panel_list_button)

            panel_list.dropEvent = lambda event, _=index: self.dropEvent(event, _)

        self.main_list.dropEvent = lambda event: self.dropEvent(event, -1)

        button_box, button_box_layout = add_widget(
            parent=self.fields_panel,
            inner_layout_class=HBoxLayout,
            outer_layout=self.fields_panel_layout,
        )
        button_box_layout.addStretch()

        ok_button = QtWidgets.QPushButton("OK")
        button_box_layout.addWidget(ok_button)
        ok_button.clicked.connect(self.handler_close)

        self.main_list.itemDoubleClicked.connect(self.handle_double_click)
        for panel_list in self.panel_list_widgets:
            panel_list.itemDoubleClicked.connect(self.handle_double_click)

    def configure(self, columns: List[DataColumn], selected_columns_list: List[List[str]]):
        clean_up_list_widget(self.main_list)
        self.columns = columns
        self.column_names = [column.column_name for column in columns]
        main_list_names = [column.column_name for column in columns]

        for panel_list, selected_columns in zip(self.panel_list_widgets, selected_columns_list):
            clean_up_list_widget(panel_list)
            for column in selected_columns:
                if column not in main_list_names:
                    continue
                main_list_names.remove(column)
                item = QListWidgetItem(column)
                item.setIcon(COLUMN_TYPE_ICONS[columns[self.column_names.index(column)].column_type])
                item.setSizeHint(QtCore.QSize(0, ITEM_HEIGHT))
                panel_list.addItem(item)

        for column in main_list_names:
            item = QListWidgetItem(column)
            item.setIcon(COLUMN_TYPE_ICONS[columns[self.column_names.index(column)].column_type])
            item.setSizeHint(QtCore.QSize(0, ITEM_HEIGHT))
            self.main_list.addItem(item)
        self.success = False

    def main_list_clicked(self):
        for button in self.panel_list_buttons:
            button.setIcon(qta.icon("ph.arrow-bend-down-right"))
            button.setText("Add")
            button.setEnabled(True)

    def panel_list_clicked(self, panel_index):
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
            event.ignore()
            return

        if isinstance(target_list, QListWidgetClickable):
            if source_list == self.main_list:
                # index != -1
                self.button_pressed(index, from_drop=True, remove=False)
            else:
                index_of_source_list = self.panel_list_widgets.index(source_list)
                if index == -1:
                    # index_of_source_list -> main
                    self.button_pressed(index_of_source_list, from_drop=True, remove=True)
                else:
                    # index_of_source_list -> index
                    # index != -1
                    selected_items = source_list.selectedItems()
                    selected_items_text = [item.text() for item in selected_items]
                    self.button_pressed(index_of_source_list, from_drop=True, remove=True)
                    selected_items_in_main_list = [
                        self.main_list.item(i)
                        for i in range(self.main_list.count())
                        if self.main_list.item(i).text() in selected_items_text
                    ]
                    for item in selected_items_in_main_list:
                        item.setSelected(True)
                    self.button_pressed(index, from_drop=True, remove=False)

        event.ignore()

    def handle_double_click(self, item):
        source_list = item.listWidget()
        if source_list == self.main_list:
            for i, panel_list in enumerate(self.panel_list_widgets):
                if panel_list.count() == 0 or not self.fields[i].allow_only_single_column:
                    self.button_pressed(i, from_double_click=True, remove=False, item=item)
                    break
        else:
            # Move item back to the main list
            panel_index = self.panel_list_widgets.index(source_list)
            self.button_pressed(panel_index, from_double_click=True, remove=True, item=item)

    def button_pressed(self, button_index, from_drop=False, from_double_click=False, remove=False, item=None):
        button = self.panel_list_buttons[button_index]
        panel_list: QListWidgetClickable = self.panel_list_widgets[button_index]
        if (
            (button.text() == "Add" and not from_drop and not from_double_click)
            or (from_drop and not remove)
            or (from_double_click and not remove)
        ):
            selected_main = [item] if from_double_click else (self.main_list.selectedItems())

            if self.fields[button_index].allow_only_single_column:
                if (panel_list.count() > 0) or (len(selected_main) > 1):
                    return

            if selected_main:
                selected_main_names = [item.text() for item in selected_main]
                selected_main_types = [
                    self.columns[self.column_names.index(item)].column_type for item in selected_main_names
                ]
                panel_type = self.fields[button_index].column_type
                if panel_type == ColumnType.NOMINAL:
                    allowed_types = [
                        ColumnType.NOMINAL,
                        ColumnType.ORDINAL,
                        ColumnType.NUMERIC,
                    ]
                elif panel_type == ColumnType.ORDINAL:
                    allowed_types = [ColumnType.ORDINAL, ColumnType.NUMERIC]
                else:
                    allowed_types = [ColumnType.NUMERIC]

                if not all([selected_main_type in allowed_types for selected_main_type in selected_main_types]):
                    icon = self.panel_list_icons[button_index]
                    old_pixmap = icon.pixmap()
                    icon.setPixmap(qta.icon("mdi.alert", color="red").pixmap(24, 24))
                    QtCore.QTimer.singleShot(50, lambda _=old_pixmap: icon.setPixmap(_))
                    return

                for item in selected_main:
                    new_item = QListWidgetItem(item.text())
                    new_item.setIcon(item.icon())
                    new_item.setSizeHint(QtCore.QSize(0, ITEM_HEIGHT))
                    panel_list.addItem(new_item)
                    self.main_list.takeItem(self.main_list.row(item))
        elif (
            (button.text() == "Remove" and not from_drop and not from_double_click)
            or (from_drop and remove)
            or (from_double_click and remove)
        ):
            selected_list = [item] if from_double_click else (panel_list.selectedItems())
            if selected_list:
                for item in selected_list:
                    new_item = QListWidgetItem(item.text())
                    new_item.setIcon(item.icon())
                    new_item.setSizeHint(QtCore.QSize(0, ITEM_HEIGHT))
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
                    new_item.setSizeHint(QtCore.QSize(0, ITEM_HEIGHT))
                    self.main_list.addItem(new_item)
        for panel_list in self.panel_list_widgets:
            panel_list.updateGeometry()

    @log_method_noarg
    def handler_close(self):
        self.widget.hide()
        self.handler_popup_close()
