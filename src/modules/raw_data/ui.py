#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import logging
from pathlib import Path

import pandas as pd
from PySide6 import QtWidgets

from src.common.decorators import log_method, log_method_noarg
from src.common.messages import MessageType
from src.common.progress import run_in_separate_thread
from src.data.data import Data
from src.data.data_manager import DATA_MANAGER
from src.modules.base.base import BaseModulePanel
from src.modules.common.result.registry import RESULTS
from src.modules.raw_data.result import RawDataStudyConfig
from src.pyside_ext.elements.button_large import LargeButton
from src.pyside_ext.elements.spacer_small import SpacerSmall
from src.pyside_ext.elements.title import Title


class RawData(BaseModulePanel):
    def setup_ui(self):
        self.elements = {
            "title": Title(label_text="Raw Data"),
            "spacer": SpacerSmall(),
            "open_sample": LargeButton(
                label_text="Replace with Sample Data",
                icon_path="msc.folder-opened",
            ),
            "open": LargeButton(
                label_text="Update Data",
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
        def main(update):
            logging.info(f"Opening {file_path}")
            update(10)
            if file_path.endswith(".csv"):
                dataframe = pd.read_csv(file_path)
            elif file_path.endswith(".xlsx"):
                dataframe = pd.read_excel(file_path, sheet_name=0)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
            update(80)
            config = RawDataStudyConfig(
                data=Data(dataframe), path=Path(file_path).resolve(), timestamp=pd.Timestamp.now()
            )
            return config

        run_in_separate_thread(
            main, progress_bar=self.root_class.settings_panel.progress_bar, on_done=self.open_file_on_done
        )

    @log_method
    def open_file_on_done(self, config):
        RESULTS[self.result_id].config = config
        DATA_MANAGER.set_raw_data_result_id(self.result_id)
        self.root_class.main_area_panel.refresh_result(self.result_id)
        self.root_class.set_current_file_path(None)

    @log_method
    def handler(self, message):
        if message.message_type == MessageType.CLICKED:
            if message.caller_id == "open":
                self.open_handler()
            elif message.caller_id == "open_sample":
                self.open_file("./data.csv")
            return
        super().handler(message)
