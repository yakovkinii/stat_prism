#
#  Copyright (c) 2023 -- 2025 StatPrism Team. All rights reserved.
#

import logging
from typing import TYPE_CHECKING

from src.common.decorators import log_method, log_method_noarg
from src.common.elements.button.small_button import SmallButton
from src.common.elements.column_color_selector.column_color_selector import ColumnColorSelector
from src.common.elements.title.title import Title
from src.common.messages import MessageType
from src.settings_panel.panels.base.base import BasePanel
from src.settings_panel.panels.registry import PanelRegistry

if TYPE_CHECKING:
    pass


class Columns(BasePanel):
    def setup_ui(self):
        self.elements = {
            "title2": Title(
                label_text="Properties of Selected Columns",
            ),
            "color": ColumnColorSelector(),
            "add_col": SmallButton(
                label_text="Add",
                icon_path="mdi.table-column-plus-after",
            ),
            "delete_col": SmallButton(
                label_text="Delete",
                icon_path="mdi.table-column-remove",
            ),
            "invert": SmallButton(
                label_text="Invert",
                icon_path="ri.arrow-up-down-line",
            ),
            "summate": SmallButton(
                label_text="Summate",
                icon_path="mdi.sigma",
            ),
        }

        self.setup(stretch=True)

    @log_method
    def configure(self, column_indexes, caller_index=None):
        self.column_indexes = column_indexes
        self.caller_index = caller_index

        all_numeric = all([self.tabledata.get_column_dtype(index) in ["int", "float"] for index in column_indexes])
        self.elements["invert"].widget.setEnabled(all_numeric)
        self.elements["summate"].widget.setEnabled(all_numeric)

    @log_method_noarg
    def inverse_handler(self):
        PanelRegistry.INVERSE.ui_instance.configure(
            column_indexes=self.column_indexes, caller_index=self.stacked_widget_index
        )
        self.root_class.action_activate_panel_by_index(PanelRegistry.INVERSE.settings_stacked_widget_index)

    @log_method_noarg
    def summate_handler(self):
        column_names = [self.tabledata.get_column_name(index) for index in self.column_indexes]
        df = self.tabledata.get_columns(column_names)

        self.tabledata.add_column(max(self.column_indexes))
        self.tabledata.set_column(max(self.column_indexes) + 1, df.sum(axis=1))
        self.root_class.action_select_table_column(max(self.column_indexes) + 1)
        self.root_class.action_activate_column_panel(max(self.column_indexes) + 1)

    @log_method_noarg
    def add_column_handler(self):
        self.tabledata.add_column(max(self.column_indexes))
        self.root_class.action_select_table_column(max(self.column_indexes) + 1)
        self.root_class.action_activate_column_panel(max(self.column_indexes) + 1)

    @log_method_noarg
    def delete_column_handler(self):
        self.tabledata.delete_columns(self.column_indexes)

        new_index = min(self.column_indexes)

        if self.tabledata.columnCount() == 0:
            self.root_class.action_activate_home_panel()
            return
        if self.tabledata.columnCount() > new_index:
            self.root_class.action_select_table_column(new_index)
            self.root_class.action_activate_column_panel(new_index)
            return

        self.root_class.action_select_table_column(new_index - 1)
        self.root_class.action_activate_column_panel(new_index - 1)

    @log_method
    def color_pressed(self, color: int):
        logging.info(f"color {color} pressed")
        previous_colors = []
        for index in self.column_indexes:
            previous_colors.append(self.tabledata.get_column_color(index))

        if all([color == previous_color for previous_color in previous_colors]):
            color = None

        for index in self.column_indexes:
            self.tabledata.set_column_color(index, color)

    @log_method
    def handler(self, message):
        if message.message_type == MessageType.CLICKED:
            if message.caller_id == "add_col":
                self.add_column_handler()
            elif message.caller_id == "delete_col":
                self.delete_column_handler()
            elif message.caller_id == "invert":
                self.inverse_handler()
            elif message.caller_id == "summate":
                self.summate_handler()
            elif message.caller_id == "color":
                self.color_pressed(message.payload)
            else:
                super().handler(message)

        else:
            super().handler(message)
