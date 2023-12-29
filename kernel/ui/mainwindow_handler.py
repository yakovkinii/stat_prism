import logging
import os
import tempfile

import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from kernel.constants import DESCRIPTIVE_INDEX, HOME_INDEX, OUTPUT_WIDTH
from kernel.misc import load_data_to_table
from kernel.ui.mainwindow import MainWindow


class MainWindowHandler(QtWidgets.QMainWindow, MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


        self.actionAbout.triggered.connect(self.about_handler)
        self.study_frame.home_panel.OpenFileButton.pressed.connect(self.open_handler)
        self.study_frame.home_panel.DescriptiveStatisticsButton.pressed.connect(
            self.select_descriptive_statistics_handler
        )

        self.results_frame.browser.setMinimumWidth(OUTPUT_WIDTH)
        self.study_frame.descriptive_panel.HomeButton.pressed.connect(
            self.home_button_handler
        )
        self.study_frame.home_panel.SaveReportButton.pressed.connect(self.save_handler)

        self.study_frame.descriptive_panel.actionTriggerUpdate.triggered.connect(self.process_descriptive)

        self.df = None
        self.output = ""
        self.study_frame.stackedWidget.setCurrentIndex(0)
        self.current_index = 0
        self.results = []
        self.collapse_results()

    def about_handler(self):
        QMessageBox.about(
            self,
            "StatPrism",
            "StatPrism Professional \n" "Version: 0.1 \n" "(C) 2023 I.Y. and A.B.",
        )

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
        self.study_frame.home_panel.SaveReportButton.setDown(False)

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
            load_data_to_table(
                dataframe=self.df, table_widget=self.table_frame.tableWidget_2
            )
        self.set_current_index(HOME_INDEX)
        self.study_frame.home_panel.OpenFileButton.setDown(False)

    def set_current_index(self, i: int):
        logging.info(f"Setting current index to {i}")
        self.study_frame.stackedWidget.setCurrentIndex(i)
        self.current_index = i

    def select_descriptive_statistics_handler(self):
        logging.info("Selecting descriptive statistics")
        if self.df is None:
            logging.warning("Ignoring: Empty table")
            return

        self.set_current_index(DESCRIPTIVE_INDEX)
        self.study_frame.descriptive_panel.listWidget_all_columns.clear()
        numeric_columns = []
        for column in self.df.columns:
            if self.df[column].dtype.kind in "biufc":  # numeric
                numeric_columns.append(column)
        self.study_frame.descriptive_panel.listWidget_all_columns.addItems(
            numeric_columns
        )
        self.study_frame.descriptive_panel.listWidget_selected_columns.clear()

    def process_descriptive(self):
        self.output = self.study_frame.descriptive_panel.process_descriptive(self.df)
        self.update_browser()

    def collapse_results(self):
        self.splitter.setSizes(
            [1, 0, 1]
        )  # cannot use actual sizes because the frame is not fully loaded yet

    def show_browser(self):
        # set browser size
        sizes = self.splitter.sizes()
        if sizes[1] == 0:
            self.splitter.setSizes([sizes[0] - OUTPUT_WIDTH, OUTPUT_WIDTH, sizes[2]])

    def update_browser(self):
        self.results_frame.update_browser(self.output)
        self.show_browser()