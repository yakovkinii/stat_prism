#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import logging
from typing import TYPE_CHECKING

from PySide6 import QtWidgets
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMessageBox

from src.about import version
from src.common.constant import MDASH, NDASH
from src.common.decorators import log_method, log_method_noarg
from src.common.messages import MessageType
from src.modules.common.result.registry import RESULTS, get_unique_result_id
from src.modules.registry import ModuleRegistry
from src.pyside_ext.elements.button_large import LargeButton
from src.pyside_ext.elements.spacer import Spacer
from src.settings_panel.panels.base import BasePanel
from src.settings_panel.registry import PanelRegistry

if TYPE_CHECKING:
    pass


class Home(BasePanel):
    def setup_ui(self):
        self.elements = {
            "raw_data": LargeButton(
                label_text="Raw Data",
                icon_path="ri.file-text-line",
            ),
            "data_processing": LargeButton(
                label_text="Data Processing",
                icon_path="ri.file-edit-line",
            ),
            "data_analysis": LargeButton(
                label_text="Data Analysis",
                icon_path="ri.bar-chart-line",
            ),
            "spacer": Spacer(),
            "about": LargeButton(
                label_text="About",
                icon_path="ri.questionnaire-line",
            ),
        }

        self.setup(stretch=True)

    @log_method_noarg
    def open_handler(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.widget,
            "Open File",
            "",
            "Supported Files (*.sp *.xlsx *.csv);;All Files (*)",
        )

        if not file_path:
            logging.info("No file selected")
            return
        self.open_file(file_path)

    @log_method_noarg
    def about_handler(self):
        msg_box = QMessageBox()

        msg_box.setWindowTitle("About StatPrism")
        msg_box.setText(
            f"StatPrism {MDASH} version {version} (Developer Edition)\n"
            "\n"
            "This version of StatPrism is intended for internal testing only.\n"
            "\n"
            "This software is in development and is provided as is, without any guarantees.\n"
            "\n"
            f"Copyright 2023 {NDASH} 2025 StatPrism Team:\n"
            f"Ivan Yakovkin (software development)\n"
            f"Alexandra Balashevych (model design)\n"
        )

        msg_box.setWindowIcon(QIcon(":/mat/resources/StatPrism_icon_small.ico"))
        msg_box.setIconPixmap(QIcon(":/mat/resources/Icon.ico").pixmap(128, 128))
        msg_box.exec_()

    @log_method
    def handler(self, message):
        if message.message_type == MessageType.CLICKED:
            if message.caller_id == "about":
                return self.about_handler()
            elif message.caller_id == "raw_data":
                module = ModuleRegistry.RAW_DATA.value

                result_id = get_unique_result_id()
                RESULTS[result_id] = module.result_class(
                    unique_id=result_id,
                    settings_panel_index=module.settings_stacked_widget_index,
                    config=module.config_class(),
                )
                self.root_class.main_area_panel.add_raw_data(result_id=result_id)

                module.ui_instance.configure(result_id=result_id)
                return self.root_class.action_activate_panel_by_index(module.settings_stacked_widget_index)
            elif message.caller_id == "data_processing":
                return self.root_class.action_activate_panel_by_index(
                    PanelRegistry.SELECT_DATA_PROCESSING.settings_stacked_widget_index
                )
            elif message.caller_id == "data_analysis":
                return self.root_class.action_activate_panel_by_index(
                    PanelRegistry.SELECT_DATA_ANALYSIS.settings_stacked_widget_index
                )
        return super().handler(message)
