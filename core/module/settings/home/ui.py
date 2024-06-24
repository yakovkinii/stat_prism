import logging
import pickle
import tempfile
from typing import TYPE_CHECKING

import pandas as pd
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QVBoxLayout

from core.globals.data import data, Data
from core.globals.debug import DEBUG_LAYOUT
from core.globals.result import result_container
from core.module.settings.base.elements import BigAssButton, Spacer, EditableTitle
from core.module.settings.base.ui import BaseSettingsPanel
from core.ui.common.common_ui import create_label, create_tool_button_qta
from core.registry.constants import NO_RESULT_SELECTED
from core.ui.common.utility import button_y
from core.registry.utility import get_next_valid_result_id, log_method, select_result

from models.correlation.objects import CorrelationResult
from models.descriptive.objects import DescriptiveResult
import zipfile

if TYPE_CHECKING:
    from core.ui.ui import MainWindowClass


class Home(BaseSettingsPanel):
    def __init__(self, parent_widget, parent_class, root_class,stacked_widget_index):
        # Setup
        super().__init__(parent_widget, parent_class, root_class,stacked_widget_index, False)

        self.elements = {
            # 'title': EditableTitle(
            #     parent_widget=self.widget_for_elements,
            #     label_text="Title lorem ipsum trololo lorem ipsum trololo #2",
            #     handler=self.finish_editiong,
            # ),
            "open":  BigAssButton(
                parent_widget=self.widget_for_elements,
                label_text="Open File",
                icon_path="msc.folder-opened",
                handler=self.open_handler
            ),
            "save":  BigAssButton(
                parent_widget=self.widget_for_elements,
                label_text="Save Report",
                icon_path="fa.save",
                handler=self.save_handler
            ),
            'spacer': Spacer(
                parent_widget=self.widget_for_elements,
            ),


        }

        self.place_elements()

    @log_method
    def create_descriptive(self):
        result_id = get_next_valid_result_id()
        result_container.results[result_id] = DescriptiveResult(result_id=result_id)
        select_result(result_id)
        self.study_instance.mainwindow_instance.actionUpdateStudyFrame.trigger()
        # self.study_instance.parent_class.actionUpdateResultsFrame.trigger()

    @log_method
    def create_correlation(self):
        result_id = get_next_valid_result_id()
        result_container.results[result_id] = CorrelationResult(result_id=result_id)
        select_result(result_id)
        self.study_instance.mainwindow_instance.actionUpdateStudyFrame.trigger()
        # self.study_instance.parent_class.actionUpdateResultsFrame.trigger()

    @log_method
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
        if file_path:
            if file_path.endswith(".csv"):
                data.load(pd.read_csv(file_path))
            elif file_path.endswith(".xlsx"):
                try:
                    data.load(pd.read_excel(file_path, sheet_name=0))
                except Exception as e:
                    logging.error(str(e))
            elif file_path.endswith(".sp"):
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Extract all files
                    with zipfile.ZipFile(file_path, 'r') as zipf:
                        zipf.extractall(temp_dir)

                    with open(f'{temp_dir}/result_container.pkl', 'rb') as file:
                        result_container.results = pickle.load(file).results

                    data.load(pd.read_parquet(f'{temp_dir}/data.df.parquet'))
                    select_result(NO_RESULT_SELECTED)
                    self.root_class.actionUpdateResultsFrame.trigger()
            else:
                logging.error('Not supported file type')

        if data.df is not None:
            select_result(NO_RESULT_SELECTED)
            # data_selected.df = data.df.copy()
            # data_selected.filter = ""
            # self.root_class.actionUpdateStudyFrame.trigger()
            # self.root_class.actionUpdateTableFrame.trigger()
            self.root_class.action_update_data_panel()
            # self.DescriptiveStatisticsButton.setEnabled(True)
            # self.CorrelationButton.setEnabled(True)

        # self.OpenFileButton.setDown(False)

    def save_handler(self):
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self.widget,
            "Chose",
            "",
            "StatPrism project (*.sp);;",
            options=options,
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            data.df.to_parquet(f'{temp_dir}/data.df.parquet')
            # Save metadata

            # with open(f'{temp_dir}/result_container.results.json', 'w') as meta_file:
            #     json.dump(result_container.results, meta_file)
            with open(f'{temp_dir}/result_container.pkl', 'wb') as file:
                pickle.dump(result_container, file)
            # Zip all files
            with zipfile.ZipFile(file_path, 'w') as zipf:
                zipf.write(f'{temp_dir}/data.df.parquet', f'data.df.parquet')
                zipf.write(f'{temp_dir}/result_container.pkl', 'result_container.pkl')

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