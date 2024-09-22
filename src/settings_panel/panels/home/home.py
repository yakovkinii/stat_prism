import logging
import pickle
import tempfile
import zipfile
from typing import TYPE_CHECKING

import pandas as pd
from PySide6 import QtWidgets
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMessageBox

from src.about import version
from src.common.constant import MDASH, NDASH
from src.common.decorators import log_method, log_method_noarg
from src.common.elements.button.large_button import LargeButton
from src.common.elements.logo.logo import Logo
from src.common.elements.spacer.spacer import Spacer
from src.common.messages import MessageType
from src.common.result.registry import RESULTS
from src.settings_panel.panels.base.base import BasePanel
from src.settings_panel.panels.registry import PanelRegistry

if TYPE_CHECKING:
    pass


class Home(BasePanel):
    def setup_ui(self):
        self.elements = {
            "open_sample": LargeButton(
                label_text="Open Sample Data",
                icon_path="msc.folder-opened",
            ),
            "open": LargeButton(
                label_text="Open / Import",
                icon_path="msc.folder-opened",
            ),
            "about": LargeButton(
                label_text="About",
                icon_path="ri.questionnaire-line",
            ),
            "spacer": Spacer(),
            "logo": Logo(),
        }

        self.setup(stretch=True)
        self.elements["logo"].widget.hide()

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

        if not self.root_class.data_panel.tabledata.get_data().empty:
            # ask to save current project
            # need yes/no/cancel dialog
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Save project?")
            msg_box.setText("Do you want to save the current project?")
            msg_box.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)
            ret = msg_box.exec_()
            if ret == QMessageBox.StandardButton.Cancel:
                return
            elif ret == QMessageBox.StandardButton.Yes:
                self.save_handler()

        if file_path.endswith(".csv"):
            dataframe = pd.read_csv(file_path)

            self.root_class.results_panel.display_none()
            self.root_class.result_selector_panel.delete_all_results()
            RESULTS.clear()

            self.root_class.data_panel.tabledata.load_data(dataframe)
        elif file_path.endswith(".xlsx"):
            dataframe = pd.read_excel(file_path, sheet_name=0)

            self.root_class.results_panel.display_none()
            self.root_class.result_selector_panel.delete_all_results()
            RESULTS.clear()

            self.root_class.data_panel.tabledata.load_data(dataframe)
        elif file_path.endswith(".sp"):
            with tempfile.TemporaryDirectory() as temp_dir:
                self.root_class.results_panel.display_none()
                self.root_class.result_selector_panel.delete_all_results()
                RESULTS.clear()

                # Extract all files
                with zipfile.ZipFile(file_path, "r") as zipf:
                    zipf.extractall(temp_dir)

                self.tabledata.load_data(pd.read_parquet(f"{temp_dir}/tabledata_df.parquet"))

                with open(f"{temp_dir}/tabledata_column_flags.pkl", "rb") as file:
                    self.tabledata.load_flags(pickle.load(file))

                with open(f"{temp_dir}/results.pkl", "rb") as file:
                    results = pickle.load(file)
                    for result in results.values():
                        RESULTS[result.unique_id] = result
                        self.root_class.result_selector_panel.add_result(result.unique_id)

        else:
            logging.error("Not supported file type")

        self.root_class.action_activate_panel_by_index(PanelRegistry.BLANK.settings_stacked_widget_index)
        self.root_class.action_activate_data_panel()
        self.root_class.action_hide_result_selector()
        logging.info(f"Opened {file_path}")

    @log_method_noarg
    def save_handler(self):
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self.widget,
            "Chose",
            "",
            "StatPrism project (*.sp);;",
        )
        if not file_path:
            return

        with tempfile.TemporaryDirectory() as temp_dir:
            self.tabledata.get_data().to_parquet(f"{temp_dir}/tabledata_df.parquet")
            with open(f"{temp_dir}/tabledata_column_flags.pkl", "wb") as file:
                pickle.dump(self.tabledata.get_flags(), file)
            with open(f"{temp_dir}/results.pkl", "wb") as file:
                pickle.dump(RESULTS, file)
            # Zip all files
            with zipfile.ZipFile(file_path, "w") as zipf:
                zipf.write(f"{temp_dir}/tabledata_df.parquet", "tabledata_df.parquet")
                zipf.write(f"{temp_dir}/tabledata_column_flags.pkl", "tabledata_column_flags.pkl")
                zipf.write(f"{temp_dir}/results.pkl", "results.pkl")

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
            f"Copyright 2023 {NDASH} 2024"
        )

        msg_box.setWindowIcon(QIcon(":/mat/resources/StatPrism_icon_small.ico"))
        msg_box.setIconPixmap(QIcon(":/mat/resources/Icon.ico").pixmap(128, 128))
        msg_box.exec_()

    @log_method
    def handler(self, message):
        if message.message_type == MessageType.CLICKED:
            if message.caller_id == "open":
                self.open_handler()
            elif message.caller_id == "open_sample":
                self.root_class.data_panel.tabledata.load_data(pd.read_csv("./data.csv"))
                self.root_class.splitter.setSizes([1, 1])
                self.root_class.action_activate_panel_by_index(PanelRegistry.BLANK.settings_stacked_widget_index)

            elif message.caller_id == "save":
                self.save_handler()
            elif message.caller_id == "about":
                self.about_handler()
            return
        super().handler(message)
