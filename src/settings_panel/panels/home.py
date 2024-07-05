import json
import logging
import pickle
import tempfile
import zipfile
from typing import TYPE_CHECKING

import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox

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
            # 'title': EditableTitle(
            #     parent_widget=self.widget_for_elements,
            #     label_text="Title lorem ipsum trololo lorem ipsum trololo #2",
            #     handler=self.finish_editiong,
            # ),
            "open": BigAssButton(
                parent_widget=self.widget_for_elements,
                label_text="Open File",
                icon_path="msc.folder-opened",
                handler=self.open_handler,
            ),
            "save": BigAssButton(
                parent_widget=self.widget_for_elements,
                label_text="Save Report",
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

    @log_method_noarg
    def open_handler(self):
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.widget,
            "Open File",
            "",
            "Supported Files (*.sp *.xlsx *.csv);;All Files (*)",
            options=options,
        )
        logging.info(f"Opening {file_path}")
        dataframe = None
        if file_path:
            if file_path.endswith(".csv"):
                dataframe = pd.read_csv(file_path)
            elif file_path.endswith(".xlsx"):
                dataframe = pd.read_excel(file_path, sheet_name=0)
            elif file_path.endswith(".sp"):
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Extract all files
                    with zipfile.ZipFile(file_path, "r") as zipf:
                        zipf.extractall(temp_dir)

                    self.tabledata.load_data(pd.read_parquet(f"{temp_dir}/tabledata_df.parquet"))
                    with open(f"{temp_dir}/tabledata_column_flags.pkl", "rb") as file:
                        self.tabledata.load_flags(pickle.load(file))
            else:
                logging.error("Not supported file type")

        if dataframe is not None:
            self.root_class.data_panel.tabledata.load_data(dataframe)

        self.elements["open"].button.setDown(False)
        logging.info(f"Opened {file_path}")

    @log_method_noarg
    def save_handler(self):
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self.widget,
            "Chose",
            "",
            "StatPrism project (*.sp);;",
            options=options,
        )
        if not file_path:
            return

        with tempfile.TemporaryDirectory() as temp_dir:
            self.tabledata.get_data().to_parquet(f"{temp_dir}/tabledata_df.parquet")
            # Save metadata
            # with open(f'{temp_dir}/tabledata_column_flags.json', 'w') as meta_file:
            #     json.dump(.results, meta_file)
            with open(f"{temp_dir}/tabledata_column_flags.pkl", "wb") as file:
                pickle.dump(self.tabledata.get_flags(), file)
            # Zip all files
            with zipfile.ZipFile(file_path, "w") as zipf:
                zipf.write(f"{temp_dir}/tabledata_df.parquet", "tabledata_df.parquet")
                zipf.write(f"{temp_dir}/tabledata_column_flags.pkl", "tabledata_column_flags.pkl")

        # def load_project(filename):
        #     # Temporary directory to extract files
        #     temp_dir = 'temp_project_files'
        #     os.makedirs(temp_dir, exist_ok=True)
        #
        #     # Extract all files
        #     with zipfile.ZipFile(filename, 'r') as zipf:
        #         zipf.extractall(temp_dir)
        #
        #     # Load metadata
        #     with open(os.path.join(temp_dir, 'metadata.json'), 'r') as meta_file:
        #         metadata = json.load(meta_file)
        #
        #     # Load dataframes
        #     dataframes = []
        #     for file in sorted(os.listdir(temp_dir)):
        #         if file.startswith('dataframe_') and file.endswith('.pkl'):
        #             df = pd.read_pickle(os.path.join(temp_dir, file))
        #             dataframes.append(df)
        #
        #     # Clean up temporary files
        #     for file in os.listdir(temp_dir):
        #         os.remove(os.path.join(temp_dir, file))
        #     os.rmdir(temp_dir)
        #
        #     return dataframes, metadata

    @log_method_noarg
    def about_handler(self):
        QMessageBox.about(
            self.widget,
            "About StatPrism",
            "StatPrism - Developer edition\n"
            "Version: 0.2\n"
            "\n"
            "This version of StatPrism is intended for developers only.\n"
            "\n"
            "StatPrism is a statistical software for data analysis.\n"
            "It is designed to be user-friendly and powerful.\n"
            "\n"
            "This software is in development and may contain bugs.\n"
            "The software is provided as is, without any guarantees.\n"
            "Please report any issues to the developers.\n"
            "\n"
            "Developed by: StatPrism team\n"
            "Copyright 2023 - 2024",
        )
