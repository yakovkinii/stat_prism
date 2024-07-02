import logging
import pickle
import tempfile
from typing import TYPE_CHECKING

import pandas as pd
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QVBoxLayout

from core.globals.debug import DEBUG_LAYOUT
from core.globals.result import result_container
from core.module.settings.base.elements import BigAssButton, Spacer, EditableTitle, EditableTitleWordWrap, Title, \
    MediumAssButton, ColumnColorSelector
from core.module.settings.base.ui import BaseSettingsPanel
from core.panels.common.common_ui import create_label, create_tool_button_qta
from core.registry.constants import NO_RESULT_SELECTED
from core.panels.common.utility import button_y
from core.registry.utility import get_next_valid_result_id, log_method, select_result, log_method_noarg

from models.correlation.objects import CorrelationResult
from models.descriptive.objects import DescriptiveResult
import zipfile

if TYPE_CHECKING:
    from core.panels.ui import MainWindowClass


class Summate(BaseSettingsPanel):
    def __init__(self, parent_widget, parent_class, root_class, stacked_widget_index):
        # Setup
        super().__init__(parent_widget, parent_class, root_class, stacked_widget_index)

        self.column_indexes = None
        self.caller_index = None
        self.elements = {
            "title2": Title(
                parent_widget=self.widget_for_elements,
                label_text="Summate",
            ),
            # "color": ColumnColorSelector(
            #     parent_widget=self.widget_for_elements,
            #     handler=self.color_pressed,
            # ),

            # "title": EditableTitleWordWrap(
            #     parent_widget=self.widget_for_elements,
            #     label_text="Title lorem ipsum trololo lorem ipsum trololo #1",
            #     handler=self.finish_editing_title,
            # ),
            "invert": MediumAssButton(
                parent_widget=self.widget_for_elements,
                label_text="Invert\ncolumn ",
                icon_path="ri.arrow-up-down-line",
                handler=self.inverse_handler,
            ),
            "add_col": MediumAssButton(
                parent_widget=self.widget_for_elements,
                label_text="Add",
                icon_path="mdi.table-column-plus-after",
                handler=self.add_column_handler,
            ),
            "delete_col": MediumAssButton(
                parent_widget=self.widget_for_elements,
                label_text="Delete columns",
                icon_path="mdi.table-column-remove",
                handler=self.delete_column_handler,
            ),
        }

        self.place_elements()

    @log_method
    def configure(self, column_indexes, caller_index=None):
        self.column_indexes = column_indexes
        self.caller_index = caller_index

        all_numeric = True
        for index in column_indexes:
            if self.tabledata.get_column_dtype(index) not in ['int']:
                all_numeric = False
                break
        self.elements["invert"].widget.setEnabled(all_numeric)

    @log_method_noarg
    def inverse_handler(self):
        self.root_class.settings_panel.inverse_panel.configure(
            column_index=self.column_indexes, caller_index=self.stacked_widget_index
        )

        self.root_class.action_activate_panel_by_index(self.root_class.settings_panel.inverse_panel_index)

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

        self.root_class.action_select_table_column(new_index-1)
        self.root_class.action_activate_column_panel(new_index-1)

    @log_method
    def color_pressed(self, color:int):
        logging.info(f"color {color} pressed")
        previous_colors = []
        for index in self.column_indexes:
            previous_colors.append(self.tabledata.get_column_color(index))

        if all([color == previous_color for previous_color in previous_colors]):
            color = None

        for index in self.column_indexes:
            self.tabledata.set_column_color(index, color)

