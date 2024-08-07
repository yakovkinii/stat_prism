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
from src.common.constant import MDASH
from src.common.custom_widget_containers import BigAssButton, Spacer
from src.common.decorators import log_method_noarg
from src.settings_panel.panels.base import BaseSettingsPanel

if TYPE_CHECKING:
    pass


class Home(BaseSettingsPanel):
    def __init__(self, parent_widget, parent_class, root_class, stacked_widget_index):
        # Setup
        super().__init__(parent_widget, parent_class, root_class, stacked_widget_index, False)

        self.elements = {
            "open": BigAssButton(
                parent_widget=self.widget_for_elements,
                label_text="Open",
                icon_path="msc.folder-opened",
                handler=self.open_handler,
            ),
            "save": BigAssButton(
                parent_widget=self.widget_for_elements,
                label_text="Save",
                icon_path="fa.save",
                handler=self.save_handler,
            ),
            "spacer": Spacer(
                parent_widget=self.widget_for_elements,
            ),
            "about": BigAssButton(
                parent_widget=self.widget_for_elements,
                label_text="About",
                icon_path="ri.questionnaire-line",
                handler=self.about_handler,
            ),
        }

        self.place_elements()

    @log_method_noarg
    def open_handler(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.widget,
            "Open File",
            "",
            "Supported Files (*.sp *.xlsx *.csv);;All Files (*)",
        )
        logging.info(f"Opening {file_path}")

        if file_path:
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
                self.root_class.data_panel.tabledata.load_data(dataframe)
                self.root_class.action_activate_home_panel()
                self.root_class.results_panel.delete_all_results()
            elif file_path.endswith(".xlsx"):
                dataframe = pd.read_excel(file_path, sheet_name=0)
                self.root_class.data_panel.tabledata.load_data(dataframe)
                self.root_class.action_activate_home_panel()
                self.root_class.results_panel.delete_all_results()
            elif file_path.endswith(".sp"):
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Extract all files
                    with zipfile.ZipFile(file_path, "r") as zipf:
                        zipf.extractall(temp_dir)

                    self.tabledata.load_data(pd.read_parquet(f"{temp_dir}/tabledata_df.parquet"))

                    with open(f"{temp_dir}/tabledata_column_flags.pkl", "rb") as file:
                        self.tabledata.load_flags(pickle.load(file))

                    self.root_class.results_panel.delete_all_results()
                    with open(f"{temp_dir}/results.pkl", "rb") as file:
                        results = pickle.load(file)
                        for result in results.values():
                            self.root_class.results_panel.add_result(result)

                self.root_class.action_activate_home_panel()
            else:
                logging.error("Not supported file type")

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
                pickle.dump(self.root_class.results_panel.results, file)
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
            "Copyright 2023 - 2024"
        )

        msg_box.setWindowIcon(QIcon(":/mat/resources/StatPrism_icon_small.ico"))
        msg_box.setIconPixmap(QIcon(":/mat/resources/Icon.ico").pixmap(128, 128))
        msg_box.exec_()
