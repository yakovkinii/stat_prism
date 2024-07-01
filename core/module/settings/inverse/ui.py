import logging
import pickle
import tempfile
from typing import TYPE_CHECKING

import pandas as pd
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QVBoxLayout

from core.globals.debug import DEBUG_LAYOUT
from core.globals.result import result_container
from core.module.settings.base.elements import BigAssButton, Spacer, EditableTitle, Title
from core.module.settings.base.ui import BaseSettingsPanel
from core.panels.common.common_ui import create_label, create_tool_button_qta
from core.panels.data_panel.data.flags import ColumnFlagsRegistry
from core.registry.constants import NO_RESULT_SELECTED
from core.panels.common.utility import button_y
from core.registry.utility import get_next_valid_result_id, log_method, select_result, log_method_noarg

from models.correlation.objects import CorrelationResult
from models.descriptive.objects import DescriptiveResult
import zipfile

if TYPE_CHECKING:
    from core.panels.ui import MainWindowClass


class Inverse(BaseSettingsPanel):
    def __init__(self, parent_widget, parent_class, root_class, stacked_widget_index):
        # Setup
        super().__init__(parent_widget, parent_class, root_class, stacked_widget_index, ok_button=True)

        self.column_index = None
        self.caller_index = None
        self.elements = {
            "title": Title(
                parent_widget=self.widget_for_elements,
                label_text="",
            ),
            # "inverse": BigAssButton(
            #     parent_widget=self.widget_for_elements,
            #     label_text="Confirm",
            #     icon_path="mdi.dots-horizontal",
            #     handler=self.inverse_handler,
            # ),
        }

        self.place_elements()

    @log_method
    def configure(self, column_index, caller_index=None):
        self.column_index = column_index
        self.caller_index = caller_index
        self.elements["title"].label.setText("Inverse " + self.tabledata.get_column_name(column_index))
        if caller_index is not None:
            self.back_button.setEnabled(True)
        else:
            self.back_button.setEnabled(False)

    @log_method_noarg
    def ok_button_pressed(self):
        column = self.tabledata.get_column(self.column_index)
        column_name = self.tabledata.get_column_name(self.column_index)
        self.tabledata.set_column(
            self.column_index,
            column.max() - (column - column.min()),
        )
        self.tabledata.toggle_column_flag(
            column_name=column_name,
            flag=ColumnFlagsRegistry.inverted,
        )
        self.activate_caller()
