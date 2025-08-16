#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import pickle
import tempfile
import zipfile
from typing import TYPE_CHECKING

from PySide6 import QtWidgets
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMessageBox

from src.about import version
from src.common.constant import MDASH, NDASH
from src.common.decorators import log_method, log_method_noarg
from src.common.messages import MessageType
from src.data.data_manager import DATA_MANAGER
from src.modules.common.result.registry import RESULTS
from src.pyside_ext.elements.button_large import LargeButton
from src.pyside_ext.elements.spacer import Spacer
from src.settings_panel.panels.base import BasePanel
from src.settings_panel.registry import PanelRegistry

if TYPE_CHECKING:
    pass


class Home(BasePanel):
    def setup_ui(self):
        self.elements = {
            "data_processing": LargeButton(
                label_text="Data Processing",
                icon_path="ri.file-edit-line",
            ),
            "data_analysis": LargeButton(
                label_text="Data Analysis",
                icon_path="ri.bar-chart-line",
            ),
            "spacer": Spacer(),
            "save": LargeButton(
                label_text="Save",
                icon_path="msc.save",
            ),
            "save_as": LargeButton(
                label_text="Save As",
                icon_path="msc.save-as",
            ),
            "about": LargeButton(
                label_text="About",
                icon_path="ri.questionnaire-line",
            ),
        }

        self.setup(stretch=True)
        self.elements["data_processing"].widget.setEnabled(False)

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

    @log_method_noarg
    def save_as_handler(self):
        self.save_handler(save_as=True)

    @log_method
    def save_handler(self, save_as=False):
        if self.root_class.current_file_path is None or save_as is True:
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self.widget,
                "Chose",
                "",
                "StatPrism project (*.sp);;",
            )
            if not file_path:
                return
        else:
            file_path = self.root_class.current_file_path

        with tempfile.TemporaryDirectory() as temp_dir:
            # DATA_MANAGER.get_raw_data().to_parquet(f"{temp_dir}/tabledata_df.parquet")
            with open(f"{temp_dir}/data_manager.pkl", "wb") as file:
                pickle.dump(DATA_MANAGER, file)
            with open(f"{temp_dir}/results.pkl", "wb") as file:
                pickle.dump(RESULTS, file)
            # Zip all files
            with zipfile.ZipFile(file_path, "w") as zipf:
                # zipf.write(f"{temp_dir}/tabledata_df.parquet", "tabledata_df.parquet")
                zipf.write(f"{temp_dir}/data_manager.pkl", "data_manager.pkl")
                zipf.write(f"{temp_dir}/results.pkl", "results.pkl")

        self.root_class.set_current_file_path(file_path)

    @log_method
    def handler(self, message):
        if message.message_type == MessageType.CLICKED:
            if message.caller_id == "about":
                return self.about_handler()
            elif message.caller_id == "data_processing":
                return self.root_class.action_activate_panel_by_index(
                    PanelRegistry.SELECT_DATA_PROCESSING.settings_stacked_widget_index
                )
            elif message.caller_id == "data_analysis":
                return self.root_class.action_activate_panel_by_index(
                    PanelRegistry.SELECT_DATA_ANALYSIS.settings_stacked_widget_index
                )
            elif message.caller_id == "save":
                return self.save_handler()
            elif message.caller_id == "save_as":
                return self.save_as_handler()

        return super().handler(message)
