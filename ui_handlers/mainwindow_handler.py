import logging
import tempfile

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
from qtconsole.mainwindow import MainWindow

from core.descriptive import run_descriptive_study
from objects.constants import DESCRIPTIVE_INDEX, OUTPUT_WIDTH, HOME_INDEX
from objects.metadata import DescriptiveStudyMetadata
from ui_design.mainwindow import UiMainWindow
import pandas as pd

from ui_utilities.mainwindow_utility import load_data_to_table, get_html_start_end
from PyQt5.QtCore import QUrl
import os


class MainWindowHandler(QtWidgets.QMainWindow, UiMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.actionOpen.triggered.connect(self.open_handler)
        self.actionDesctiptive_Statistics.triggered.connect(
            self.select_descriptive_statistics_handler
        )
        self.frame_obj.OpenFileButton.pressed.connect(self.open_handler)
        self.frame_obj.DescriptiveStatisticsButton.pressed.connect(
            self.select_descriptive_statistics_handler
        )
        self.frame_obj.DownButton.pressed.connect(self.add_columns_to_selected)
        self.frame_obj.UpButton.pressed.connect(self.remove_columns_from_selected)
        self.frame2_obj.browser.setMinimumWidth(OUTPUT_WIDTH)
        self.frame_obj.HomeButton.pressed.connect(self.home_button_handler)
        self.frame_obj.SaveReportButton.pressed.connect(self.save_handler)
        self.frame_obj.checkBox.stateChanged.connect(self.process_descriptive)
        self.frame_obj.checkBox_missing.stateChanged.connect(self.process_descriptive)
        self.frame_obj.checkBox_3.stateChanged.connect(self.process_descriptive)
        self.frame_obj.checkBox_4.stateChanged.connect(self.process_descriptive)
        self.frame_obj.checkBox_6.stateChanged.connect(self.process_descriptive)
        self.frame_obj.checkBox_7.stateChanged.connect(self.process_descriptive)
        self.frame_obj.checkBox_8.stateChanged.connect(self.process_descriptive)
        self.frame_obj.checkBox_9.stateChanged.connect(self.process_descriptive)

        self.temp_file = None
        self.df = None
        self.output = ""
        self.frame_obj.stackedWidget.setCurrentIndex(0)
        self.current_index = 0
        self.results = []
        self.collapse_results()

    def home_button_handler(self):
        self.set_current_index(HOME_INDEX)

    def save_handler(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File", "", "HTML Files (*.html);;All Files (*)", options=options
        )

        if file_path:
            # If the user doesn't add the .html extension, add it for them
            if not file_path.lower().endswith(".html"):
                file_path += ".html"
            with open(file_path, "wt") as f:
                f.write(self.output)
        self.SaveReportButton.setDown(False)

    def open_handler(self):
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open CSV File",
            "",
            "Excel Files (*.xlsx *.csv);;All Files (*)",
            options=options,
        )
        logging.info(f"Opening {file_path}")
        if file_path:
            if file_path.endswith(".csv"):
                self.df = pd.read_csv(file_path)
            elif file_path.endswith(".xlsx"):
                try:
                    self.df = pd.read_excel(file_path, sheet_name=0)
                except Exception as e:
                    logging.error(str(e))
        if self.df is not None:
            load_data_to_table(dataframe=self.df, table_widget=self.table.tableWidget_2)
        self.set_current_index(HOME_INDEX)
        self.frame_obj.OpenFileButton.setDown(False)

    def set_current_index(self, i: int):
        logging.info(f"Setting current index to {i}")
        self.frame_obj.stackedWidget.setCurrentIndex(i)
        self.current_index = i

    def select_descriptive_statistics_handler(self):
        logging.info("Selecting descriptive statistics")
        if self.df is None:
            logging.warning("Ignoring: Empty table")
            return

        self.set_current_index(DESCRIPTIVE_INDEX)
        self.listWidget.clear()
        numeric_columns = []
        for column in self.df.columns:
            if self.df[column].dtype.kind in "biufc":  # numeric
                numeric_columns.append(column)
        self.listWidget.addItems(numeric_columns)
        self.listWidget_2.clear()

    def add_columns_to_selected(self):
        w1 = self.listWidget.selectedItems()
        w1 = [c.text() for c in w1]
        selected = [
            self.listWidget_2.item(i).text() for i in range(self.listWidget_2.count())
        ]
        for item in w1:
            if item not in selected:
                self.listWidget_2.addItems([item])
        self.process_descriptive()

    def remove_columns_from_selected(self):
        for item in self.listWidget_2.selectedItems():
            self.listWidget_2.takeItem(self.listWidget_2.row(item))
        self.process_descriptive()

    def process_descriptive(self):
        logging.info("Running descriptive statistics")

        if self.current_index != DESCRIPTIVE_INDEX:
            logging.error("aborting: wrong index")
            return

        metadata = DescriptiveStudyMetadata(
            selected_columns=[
                self.listWidget_2.item(i).text()
                for i in range(self.listWidget_2.count())
            ],
            n=self.checkBox.checkState(),
            missing=self.checkBox_missing.checkState(),
            mean=self.checkBox_3.checkState(),
            median=self.checkBox_4.checkState(),
            stddev=self.checkBox_6.checkState(),
            variance=self.checkBox_7.checkState(),
            minimum=self.checkBox_8.checkState(),
            maximum=self.checkBox_9.checkState(),
        )
        html_start, html_end = get_html_start_end()
        self.output = html_start + run_descriptive_study(self.df, metadata) + html_end
        self.update_browser()

    def collapse_results(self):
        self.splitter.setSizes(
            [1, 0, 1]
        )  # cannot use actual sizes because the frame is not fully loaded yet

    def update_browser(self):
        if self.temp_file is not None:
            self.temp_file.close()
        self.temp_file = tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", delete=False, suffix=".html"
        )
        self.temp_file.write(self.output)
        self.temp_file.seek(0)
        self.browser.load(QUrl.fromLocalFile(os.path.abspath(self.temp_file.name)))

        # set browser size
        sizes = self.splitter.sizes()
        if sizes[1] == 0:
            self.splitter.setSizes([sizes[0] - OUTPUT_WIDTH, OUTPUT_WIDTH, sizes[2]])
