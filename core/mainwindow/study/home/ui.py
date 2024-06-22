import logging
import pickle
import tempfile
from typing import TYPE_CHECKING

import pandas as pd
from PyQt5 import QtCore, QtWidgets

from core.common_ui import create_label, create_tool_button_qta
from core.constants import NO_RESULT_SELECTED
from core.mainwindow.study.home.utility import button_y
from core.shared import data, result_container, data_selected
from core.utility import get_next_valid_result_id, log_method, select_result
from models.correlation.objects import CorrelationResult
from models.descriptive.objects import DescriptiveResult
import zipfile

if TYPE_CHECKING:
    from core.mainwindow.study.ui import Study


class Home:
    def __init__(self, study_instance):
        self.study_instance: Study = study_instance
        self.widget = QtWidgets.QWidget()

        self.OpenFileButton = create_tool_button_qta(
            parent=self.widget,
            button_geometry=QtCore.QRect(30, button_y(0, 0), 101, 101),
            icon_path="msc.folder-opened",
            icon_size=QtCore.QSize(80, 80),
        )

        self.SaveReportButton = create_tool_button_qta(
            parent=self.widget,
            button_geometry=QtCore.QRect(30, button_y(0, 1), 101, 101),
            icon_path="fa.save",
            icon_size=QtCore.QSize(75, 75),
        )
        # self.SaveReportButton.setEnabled(False)

        self.DescriptiveStatisticsButton = create_tool_button_qta(
            parent=self.widget,
            button_geometry=QtCore.QRect(30, button_y(1, 2), 101, 101),
            icon_path="msc.pie-chart",
            icon_size=QtCore.QSize(80, 80),
        )
        self.DescriptiveStatisticsButton.setEnabled(False)

        self.CorrelationButton = create_tool_button_qta(
            parent=self.widget,
            button_geometry=QtCore.QRect(30, button_y(1, 3), 101, 101),
            icon_path="ph.chart-line-up-light",
            icon_size=QtCore.QSize(80, 80),
        )
        self.CorrelationButton.setEnabled(False)

        self.label_open = create_label(
            parent=self.widget,
            label_geometry=QtCore.QRect(150, button_y(0, 0), 251, 101),
            font_size=14,
            alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter,
        )
        self.label_save = create_label(
            parent=self.widget,
            label_geometry=QtCore.QRect(150, button_y(0, 1), 251, 101),
            font_size=14,
            alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter,
        )

        self.label_descriptive = create_label(
            parent=self.widget,
            label_geometry=QtCore.QRect(150, button_y(1, 2), 251, 101),
            font_size=14,
            alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter,
        )

        self.label_correlation = create_label(
            parent=self.widget,
            label_geometry=QtCore.QRect(150, button_y(1, 3), 251, 101),
            font_size=14,
            alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter,
        )

        self.OpenFileButton.pressed.connect(self.open_handler)
        self.DescriptiveStatisticsButton.pressed.connect(self.create_descriptive)
        self.CorrelationButton.pressed.connect(self.create_correlation)
        self.SaveReportButton.pressed.connect(self.save_handler)

    def retranslateUI(self):
        _translate = QtCore.QCoreApplication.translate

        self.DescriptiveStatisticsButton.setText(_translate("MainWindow", "Descriptive\n" "Statistics"))
        self.label_open.setText(_translate("MainWindow", "Open File"))
        self.label_descriptive.setText(_translate("MainWindow", "Descriptive\n" "Statistics"))
        self.label_correlation.setText(_translate("MainWindow", "Correlation"))
        self.label_save.setText(_translate("MainWindow", "Save Report"))

    @log_method
    def create_descriptive(self):
        result_id = get_next_valid_result_id()
        result_container.results[result_id] = DescriptiveResult(result_id=result_id)
        select_result(result_id)
        self.study_instance.mainwindow_instance.actionUpdateStudyFrame.trigger()
        # self.study_instance.mainwindow_instance.actionUpdateResultsFrame.trigger()

    @log_method
    def create_correlation(self):
        result_id = get_next_valid_result_id()
        result_container.results[result_id] = CorrelationResult(result_id=result_id)
        select_result(result_id)
        self.study_instance.mainwindow_instance.actionUpdateStudyFrame.trigger()
        # self.study_instance.mainwindow_instance.actionUpdateResultsFrame.trigger()

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
                data.df = pd.read_csv(file_path)
            elif file_path.endswith(".xlsx"):
                try:
                    data.df = pd.read_excel(file_path, sheet_name=0)
                except Exception as e:
                    logging.error(str(e))
            elif file_path.endswith(".sp"):
                with tempfile.TemporaryDirectory() as temp_dir:
                        # Extract all files
                        with zipfile.ZipFile(file_path, 'r') as zipf:
                            zipf.extractall(temp_dir)

                        with open(f'{temp_dir}/result_container.pkl', 'rb') as file:
                            result_container.results = pickle.load(file).results

                        data.df = pd.read_parquet(f'{temp_dir}/data.df.parquet')
                        select_result(NO_RESULT_SELECTED)
                        self.study_instance.mainwindow_instance.actionUpdateResultsFrame.trigger()
            else:
                logging.error('Not supported file type')

        if data.df is not None:
            select_result(NO_RESULT_SELECTED)
            data_selected.df = data.df.copy()
            data_selected.filter = ""
            self.study_instance.mainwindow_instance.actionUpdateStudyFrame.trigger()
            self.study_instance.mainwindow_instance.actionUpdateTableFrame.trigger()
            self.DescriptiveStatisticsButton.setEnabled(True)
            self.CorrelationButton.setEnabled(True)

        self.OpenFileButton.setDown(False)

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

