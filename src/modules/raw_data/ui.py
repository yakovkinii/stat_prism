#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import logging

import pandas as pd
from PySide6 import QtWidgets
from PySide6.QtWidgets import QMessageBox

from src.common.decorators import log_method, log_method_noarg
from src.common.elements.button.large_button import LargeButton
from src.common.elements.spacer.spacer_small import SpacerSmall
from src.common.elements.title.title import Title
from src.common.messages import MessageType
from src.common.result.registry import RESULTS, get_unique_result_id
from src.data.data import Data
from src.data.data_manager import DATA_MANAGER
from src.modules.base.base import BaseModulePanel
from src.modules.raw_data.result import RawDataResult, RawDataStudyConfig


class RawData(BaseModulePanel):
    def setup_ui(self):
        self.elements = {
            "title": Title(label_text="Raw Data"),
            "spacer": SpacerSmall(),
            "open_sample": LargeButton(
                label_text="Open Sample Data",
                icon_path="msc.folder-opened",
            ),
            "open": LargeButton(
                label_text="Open / Import",
                icon_path="msc.folder-opened",
            ),
        }
        self.setup(stretch=True)

    @log_method
    def configure(self, result_id: int):
        self.configuring = True
        self.result_id = result_id
        self.set_recalculate_button_highlight(RESULTS[result_id].needs_update)
        self.configuring = False

    def recalculate(self):
        pass
    @log_method
    def handler(self, message):
        if message.message_type == MessageType.CLICKED:
            if message.caller_id == "open":
                self.open_handler()
            elif message.caller_id == "open_sample":
                # self.root_class.data_panel.tabledata.load_data(pd.read_csv("./data.csv"))
                self.open_file("./data.csv")
                # self.root_class.splitter.setSizes([1, 1])
                # self.root_class.action_activate_panel_by_index(PanelRegistry.BLANK.settings_stacked_widget_index)
            return
        super().handler(message)

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
    @log_method
    def open_file(self, file_path):
        logging.info(f"Opening {file_path}")

        # if not self.root_class.data_panel.tabledata.get_data().empty:
        #     # ask to save current project
        #     # need yes/no/cancel dialog
        #     msg_box = QMessageBox()
        #     msg_box.setWindowTitle("Save project?")
        #     msg_box.setText("Do you want to save the current project?")
        #     msg_box.setStandardButtons(
        #         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
        #     )
        #     msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)
        #     ret = msg_box.exec_()
        #     if ret == QMessageBox.StandardButton.Cancel:
        #         return
        #     elif ret == QMessageBox.StandardButton.Yes:
        #         # self.save_handler()
        #         ...

        if file_path.endswith(".csv"):
            dataframe = pd.read_csv(file_path)
            RESULTS[self.result_id].config = RawDataStudyConfig(
                    data=Data(dataframe),
                    path=file_path,
                    timestamp=pd.Timestamp.now()
                )
            DATA_MANAGER.set_raw_data_result_id(self.result_id)
            # self.root_class.main_area_panel.add_raw_data(self.result_id)
            # RESULTS.clear()
            self.root_class.main_area_panel.refresh_result(self.result_id)


            self.root_class.set_current_file_path(None)
            # self.root_class.data_panel.tabledata.load_data(dataframe)
        elif file_path.endswith(".xlsx"):
            dataframe = pd.read_excel(file_path, sheet_name=0)
            RESULTS[self.result_id].config = RawDataStudyConfig(
                    data=Data(dataframe),
                    path=file_path,
                    timestamp=pd.Timestamp.now()
                )
            DATA_MANAGER.set_raw_data_result_id(self.result_id)
            # self.root_class.main_area_panel.add_raw_data(self.result_id)
            self.root_class.main_area_panel.refresh_result(self.result_id)
            self.root_class.set_current_file_path(None)
            # self.root_class.data_panel.tabledata.load_data(dataframe)
        # elif file_path.endswith(".sp"):
        #     with tempfile.TemporaryDirectory() as temp_dir:
        #         self.root_class.results_panel.display_none()
        #         self.root_class.result_selector_panel.delete_all_results()
        #         RESULTS.clear()
        #
        #         # Extract all files
        #         with zipfile.ZipFile(file_path, "r") as zipf:
        #             zipf.extractall(temp_dir)
        #
        #         self.tabledata.load_data(pd.read_parquet(f"{temp_dir}/tabledata_df.parquet"))
        #
        #         with open(f"{temp_dir}/results.pkl", "rb") as file:
        #             results = pickle.load(file)
        #             for result in results.values():
        #                 RESULTS[result.unique_id] = result
        #                 self.root_class.result_selector_panel.add_result(result.unique_id)
        #     self.root_class.set_current_file_path(file_path)

        else:
            logging.error("Not supported file type")

        # self.root_class.action_activate_panel_by_index(PanelRegistry.BLANK.settings_stacked_widget_index)
        # self.root_class.action_activate_data_panel()
        # self.root_class.action_hide_result_selector()
        logging.info(f"Opened {file_path}")