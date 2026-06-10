#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import logging
from pathlib import Path

import pandas as pd
from PySide6 import QtWidgets

from src.common.decorators import log_method, log_method_noarg
from src.common.messages import MessageType
from src.common.progress import run_in_separate_thread
from src.data.data import Data, DataColumn
from src.data.data_manager import DATA_MANAGER
from src.pyside_ext.elements.button_large import LargeButton
from src.pyside_ext.elements.checkbox import LargeCheckbox
from src.side_area_panel.modules.base.base import BaseModulePanel
from src.side_area_panel.modules.common.result.registry import RESULTS
from src.side_area_panel.modules.common.utility import unique_name
from src.side_area_panel.modules.raw_data.raw_data_result import RawDataStudyConfig


class RawData(BaseModulePanel):
    def setup_ui(self):
        self.elements = {
            "open": LargeButton(
                label_text="Replace Data",
                icon_path="ph.arrows-clockwise",
            ),
            "add_id": LargeCheckbox(label_text="Add ID column (row number)"),
        }
        self.setup(stretch=True, label="Load Raw Data")
        self.elements["add_id"].widget.setChecked(True)

    @log_method
    def configure(self, result_id: int):
        self.configuring = True
        self.result_id = result_id
        self.elements["add_id"].widget.setChecked(getattr(RESULTS[result_id].config, "add_id", True))
        self.set_recalculate_button_highlight(RESULTS[result_id].needs_update)
        self.configuring = False

    def recalculate(self):
        pass

    def _build_data(self, config: RawDataStudyConfig) -> Data:
        data = Data.initialize_from_dataframe(config.dataframe.copy())
        if getattr(config, "add_id", True) and data.n_columns() > 0:
            index = data.columns[0].data_series.index
            name = unique_name("ID", set(data.column_names()))
            id_series = pd.Series(range(1, len(index) + 1), index=index, name=name)
            data.add_column_first(DataColumn.initialize_from_series(id_series))
        return data

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
        add_id = self.elements["add_id"].widget.isChecked()

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
                dataframe=dataframe,
                path=Path(file_path).resolve(),
                timestamp=pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                add_id=add_id,
            )
            return config

        run_in_separate_thread(
            main, progress_bar=self.root_class.settings_panel.progress_bar, on_done=self.open_file_on_done
        )

    @log_method
    def open_file_on_done(self, config):
        RESULTS[self.result_id].config = config
        RESULTS[self.result_id].data = self._build_data(config)
        DATA_MANAGER.set_raw_data_result_id(self.result_id)
        self.root_class.main_area_panel.refresh_result(self.result_id)
        self.root_class.main_area_panel.cascade_update(self.result_id)
        self.root_class.set_current_file_path(None)

    @log_method
    def handler(self, message):
        if message.message_type == MessageType.CLICKED:
            if message.caller_id == "open":
                self.open_handler()
            return
        if message.message_type == MessageType.STATE_CHANGED:
            if self.configuring:
                return
            if message.caller_id == "add_id":
                result = RESULTS[self.result_id]
                if getattr(result.config, "dataframe", None) is not None:
                    result.config.add_id = self.elements["add_id"].widget.isChecked()
                    result.data = self._build_data(result.config)
                    self.root_class.main_area_panel.refresh_result(self.result_id)
                    self.root_class.main_area_panel.cascade_update(self.result_id)
            return
        super().handler(message)
