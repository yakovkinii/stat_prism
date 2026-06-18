#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import logging
from pathlib import Path

import pandas as pd
from PySide6 import QtWidgets

from src.common.constant import ColumnType, ID_COLUMN_NAME
from src.common.decorators import log_method, log_method_noarg
from src.common.messages import MessageType
from src.common.progress import run_in_separate_thread
from src.data.data import Data, DataColumn
from src.data.data_manager import DATA_MANAGER
from src.pyside_ext.elements.button_large import LargeButton
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
        }
        self.setup(stretch=True, label="Load Raw Data")

    @log_method
    def configure(self, result_id: int):
        self.configuring = True
        self.result_id = result_id
        self.set_recalculate_button_highlight(RESULTS[result_id].needs_update)
        self.configuring = False

    def recalculate(self):
        pass

    def _build_data(self, config: RawDataStudyConfig) -> Data:
        data = Data.initialize_from_dataframe(config.dataframe.copy())
        if data.n_columns() > 0:
            # A mandatory identifier column, always named exactly ID_COLUMN_NAME and typed as ID.
            # If the loaded data already has such a column, rename that existing one out of the way.
            if ID_COLUMN_NAME in data.column_names():
                data.rename_column(ID_COLUMN_NAME, unique_name(ID_COLUMN_NAME, set(data.column_names())))
            index = data.columns[0].data_series.index
            id_series = pd.Series(range(1, len(index) + 1), index=index, name=ID_COLUMN_NAME)
            id_column = DataColumn.initialize_from_series(id_series)
            id_column.column_type = ColumnType.ID
            id_column.is_numeric = False
            data.add_column_first(id_column)
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
        super().handler(message)
