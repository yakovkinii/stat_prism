import logging
import pickle
import tempfile
from typing import TYPE_CHECKING

import pandas as pd
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QVBoxLayout

from core.globals.data import data
from core.globals.debug import DEBUG_LAYOUT
from core.globals.result import result_container
from core.module.settings.base.elements import BigAssButton, Spacer, EditableTitle
from core.module.settings.base.ui import BaseSettingsPanel
from core.ui.common.common_ui import create_label, create_tool_button_qta
from core.registry.constants import NO_RESULT_SELECTED
from core.ui.common.utility import button_y
from core.registry.utility import get_next_valid_result_id, log_method, select_result, log_method_noarg

from models.correlation.objects import CorrelationResult
from models.descriptive.objects import DescriptiveResult
import zipfile

if TYPE_CHECKING:
    from core.ui.ui import MainWindowClass


class Column(BaseSettingsPanel):
    def __init__(self, parent_widget, parent_class, root_class,stacked_widget_index):
        # Setup
        super().__init__(parent_widget, parent_class, root_class,stacked_widget_index)

        self.column_index = None
        self.caller_index=None
        self.elements = {
            'title': EditableTitle(
                parent_widget=self.widget_for_elements,
                label_text="Title lorem ipsum trololo lorem ipsum trololo #2",
                handler=self.finish_editing_title,
            ),
            "open2": BigAssButton(
                parent_widget=self.widget_for_elements,
                label_text="Inverse column",
                icon_path="mdi.dots-horizontal",
                handler=self.inverse_handler
            ),
        }

        self.place_elements()

    @log_method
    def configure(self, column_index, caller_index = None):
        self.column_index = column_index
        self.caller_index = caller_index
        self.elements['title'].label.setText(str(data.df.columns[column_index]))
        self.elements['title'].label.setCursorPosition(0)


    @log_method_noarg
    def finish_editing_title(self):
        data.df=data.df.rename(columns={data.df.columns[self.column_index]: self.elements['title'].label.text()})
        self.root_class.action_update_data_panel()

    @log_method_noarg
    def inverse_handler(self):
        self.root_class.settings_panel.inverse_panel.configure(column_index = self.column_index,
                                                               caller_index=self.stacked_widget_index)

        self.root_class.action_activate_panel_by_index(
            self.root_class.settings_panel.inverse_panel_index
        )
