#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from typing import List

import attrs
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QPoint
from PySide6.QtWidgets import (
    QVBoxLayout,
    QListWidget, QFrame,
)

from src.common.constant import ColumnType, SettingsPanelSize
from src.data.data import DataColumn
from src.pyside_ext.elements.utility.layout_helpers import (
    clean_up_list_widget,
    add_widget,
)
from src.pyside_ext.elements.utility.primitive_elements import (
    QWidgetClickable, QListWidgetClickable,
)
from src.pyside_ext.layout import VBoxLayout
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfig

ITEM_HEIGHT = 20


@attrs.define
class Field:
    name: str
    column_type: ColumnType
    reasonable_number_of_columns: int = 5
    allow_only_single_column: bool = False
    minimum_columns: int = 0


class ColumnSelectorIISPWAC(ItemInSidePanelWithAutoConfig):
    def __init__(self, fields: List[Field]):
        super().__init__()
        self.fields = fields
        self.scroll = None

    def post_init(self, label, parent_widget):
        self.label = label
        self.widget, self.layout = add_widget(
            parent=parent_widget,
            inner_layout_class=QVBoxLayout,
            widget_class=QWidgetClickable,
        )

        self.main_field_frame, self.main_field_frame_layout = add_widget(
            # parent=self.widget,
            # outer_layout=self.layout,
            inner_layout_class=VBoxLayout,
            widget_class=QFrame,
            css=css(background_color=Style.Color.BackgroundElevated,
                     border=Style.General.border,
                    )
        )
        self.main_field_frame.setFrameShape(QFrame.StyledPanel)
        self.main_field_frame.setFixedWidth(SettingsPanelSize.width)
        # self.main_field_frame.setFixedHeight(200)

        self.main_field_frame.hide()

        self.main_field, self.main_field_layout = add_widget(
            parent=self.main_field_frame,
            outer_layout=self.main_field_frame_layout,
            widget=QListWidgetClickable(self.widget),
        )
        self.main_field.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.main_field.setDragEnabled(True)
        self.main_field.setAcceptDrops(True)
        self.main_field.setDropIndicatorShown(True)
        self.main_field.setDefaultDropAction(QtCore.Qt.DropAction.MoveAction)

        self.field1, self.field1_layout = add_widget(
            parent=self.widget,
            outer_layout=self.layout,
            # inner_layout_class=QHBoxLayout,
            widget=QListWidgetClickable(self.widget),
        )
        self.field1.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.field1.setDragEnabled(True)
        self.field1.setAcceptDrops(True)
        self.field1.setDropIndicatorShown(True)
        self.field1.setDefaultDropAction(QtCore.Qt.DropAction.MoveAction)
        self.field1.clicked.connect(lambda: self.show_panel_for(self.field1))

    def configure(self, columns: List[DataColumn], selected_columns_list):
        columns_for_main = columns.copy()
        for panel_list, selected_columns in zip([self.field1], selected_columns_list):
            clean_up_list_widget(panel_list)
            panel_list.addItems(
                [selected_column.column_name for selected_column in selected_columns]
                if selected_columns not in [None, [None]]
                else []
            )
            for col_name in selected_columns:
                columns_for_main = [col for col in columns_for_main if col != col_name]

        clean_up_list_widget(self.main_field)
        self.main_field.addItems([col.column_name for col in columns_for_main])

    def inject_scroll_and_root_parent_widget(self, scroll, side_panel_root_widget, root_widget):
        self.scroll = scroll
        self.side_panel_root_widget = side_panel_root_widget
        self.scroll.verticalScrollBar().valueChanged.connect(self.reposition_panel)
        self.current_item = None
        self.main_field_frame.setParent(root_widget)
        self.root_widget = root_widget

    def show_panel_for(self, item_widget):
        self.current_item = item_widget
        self.main_field_frame.show()
        self.main_field_frame.adjustSize()
        self.reposition_panel()

    def reposition_panel(self):
        if not self.current_item or not self.main_field_frame.isVisible():
            return

        assert self.scroll is not None
        assert self.side_panel_root_widget is not None

        item_pos_in_self = self.current_item.mapTo(self.side_panel_root_widget, QPoint(0, 0))
        sidebar_pos_in_self = self.scroll.mapTo(self.side_panel_root_widget, QPoint(0, 0))

        gap = -10
        x = sidebar_pos_in_self.x() - self.main_field_frame.width() - gap

        # --- center panel on the item vertically ---
        item_h = self.current_item.height
        panel_h = self.main_field_frame.height()
        y = item_pos_in_self.y() + (item_h // 2) - (panel_h // 2)

        # clamp so it doesn't go off top/bottom of main widget
        y = max(0, min(y, self.side_panel_root_widget.height() - panel_h - 5))

        side_panel_pos = self.scroll.mapTo(self.root_widget, QPoint(0, 0))

        self.main_field_frame.move(x+side_panel_pos.x(), y+side_panel_pos.y())
        self.main_field_frame.raise_()