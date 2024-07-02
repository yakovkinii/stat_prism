import logging
import tempfile
import zipfile
from typing import TYPE_CHECKING

import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox

from src.common.custom_widget_containers import BigAssButton, Spacer, Title
from src.common.decorators import log_method_noarg
from src.settings_panel.panels.base import BaseSettingsPanel

if TYPE_CHECKING:
    pass


class SelectStudy(BaseSettingsPanel):
    def __init__(self, parent_widget, parent_class, root_class, stacked_widget_index):
        # Setup
        super().__init__(parent_widget, parent_class, root_class, stacked_widget_index)

        self.elements = {
            "title": Title(
                parent_widget=self.widget_for_elements,
                label_text="Add new study, how exciting! :)",
            ),
            "descriptive": BigAssButton(
                parent_widget=self.widget_for_elements,
                label_text="Descriptive",
                icon_path="msc.folder-opened",
                # handler=self.open_handler,
            ),
            "correlations": BigAssButton(
                parent_widget=self.widget_for_elements,
                label_text="Correlations",
                icon_path="fa.save",
                # handler=self.save_handler,
            ),
        }

        self.place_elements()

    # @log_method
    # def create_descriptive(self):
    #     result_id = get_next_valid_result_id()
    #     result_container.results[result_id] = DescriptiveResult(result_id=result_id)
    #     select_result(result_id)
    #     self.study_instance.mainwindow_instance.actionUpdateStudyFrame.trigger()
    #     # self.study_instance.parent_class.actionUpdateResultsFrame.trigger()

    # @log_method
    # def create_correlation(self):
    #     result_id = get_next_valid_result_id()
    #     result_container.results[result_id] = CorrelationResult(result_id=result_id)
    #     select_result(result_id)
    #     self.study_instance.mainwindow_instance.actionUpdateStudyFrame.trigger()
    #     # self.study_instance.parent_class.actionUpdateResultsFrame.trigger()
