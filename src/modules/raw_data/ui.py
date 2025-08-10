#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import logging
import time
from pathlib import Path

import pandas as pd
from PySide6 import QtWidgets
from PySide6.QtWidgets import QMessageBox

from src.common.decorators import log_method, log_method_noarg
from src.common.elements.button.large_button import LargeButton
from src.common.elements.spacer.spacer_small import SpacerSmall
from src.common.elements.title.title import Title
from src.common.messages import MessageType
from src.common.progress import with_progress, with_progress_bar
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
                self.start_file_with_progress("./data.csv")
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
        self.start_file_with_progress(file_path)

    @log_method
    def open_file(self, file_path):
        logging.info(f"Opening {file_path}")

        if file_path.endswith(".csv"):
            dataframe = pd.read_csv(file_path)
        elif file_path.endswith(".xlsx"):
            dataframe = pd.read_excel(file_path, sheet_name=0)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")

        RESULTS[self.result_id].config = RawDataStudyConfig(
            data=Data(dataframe), path=Path(file_path).resolve(), timestamp=pd.Timestamp.now()
        )
        DATA_MANAGER.set_raw_data_result_id(self.result_id)
        self.root_class.main_area_panel.refresh_result(self.result_id)

        self.root_class.set_current_file_path(None)

        logging.info(f"Opened {file_path}")






    @log_method
    def start_file_with_progress(self, file_path):
        def main(update):
            logging.info(f"Opening {file_path}")
            time.sleep(1)
            update(10)
            time.sleep(1)
            if file_path.endswith(".csv"):
                dataframe = pd.read_csv(file_path)
            elif file_path.endswith(".xlsx"):
                dataframe = pd.read_excel(file_path, sheet_name=0)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
            update(80)
            time.sleep(1)
            config = RawDataStudyConfig(
                data=Data(dataframe), path=Path(file_path).resolve(), timestamp=pd.Timestamp.now()
            )
            update(100)
            time.sleep(1)
            return config

        with_progress_bar(main, progress_bar=self.root_class.settings_panel.progress_bar, on_done=self.finish_file_with_progress)



    @log_method
    def finish_file_with_progress(self, config):
        RESULTS[self.result_id].config = config
        DATA_MANAGER.set_raw_data_result_id(self.result_id)
        self.root_class.main_area_panel.refresh_result(self.result_id)
        self.root_class.set_current_file_path(None)
        logging.info(f"Opened.")