import logging
import os
import tempfile

import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QMessageBox

from core.descriptive.descriptive import run_descriptive_study
from objects.constants import DESCRIPTIVE_INDEX, HOME_INDEX, OUTPUT_WIDTH
from objects.metadata import DescriptiveStudyMetadata
from ui.constructors.mainwindow import MainWindow


def get_html_start_end():
    html_start = """
    <!DOCTYPE html>
    <html lang="en">

    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Your Page Title</title>
        <style>
            /* Base Table Styles */
            table {
                border-collapse: collapse;
                font-size: 18px;
                width: 100%;
                display: block;
                overflow-x: auto;
                white-space: nowrap;
                text-align: right;
            }

            th, td {
                padding: 8px 12px;
                border: 1px solid #ddd;
                width: 50px;
                min-width: 50px;
                position:relative;
            }

            th {
                background-color: #f7f9fa;
            }

            tr:hover {
                background-color: #e5f3f8;
            }

            /* Freeze the first column */
            td:first-child, th:first-child {
                position: sticky;
                left: 0;
                z-index: 1;
                font-weight:800;
                background-color: #f7f9fa;
            }
            .hidden_first_th th:first-child {{
                visibility: hidden;
            }}
        </style>
    </head>

    <body>
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center; width:100%;">
        """
    html_end = """
    </div>
    </body>
    </html>
    """
    return html_start, html_end


def load_data_to_table(dataframe, table_widget):
    table_widget.setRowCount(dataframe.shape[0])
    table_widget.setColumnCount(dataframe.shape[1])
    table_widget.setHorizontalHeaderLabels(dataframe.columns)

    for row in dataframe.iterrows():
        for col, value in enumerate(row[1]):
            table_widget.setItem(row[0], col, QTableWidgetItem(str(value)))


class MainWindowHandler(QtWidgets.QMainWindow, MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.actionAbout.triggered.connect(self.about_handler)
        self.study_frame.home_panel.OpenFileButton.pressed.connect(self.open_handler)
        self.study_frame.home_panel.DescriptiveStatisticsButton.pressed.connect(
            self.select_descriptive_statistics_handler
        )
        self.study_frame.descriptive_panel.DownButton.pressed.connect(
            self.add_columns_to_selected
        )
        self.study_frame.descriptive_panel.UpButton.pressed.connect(
            self.remove_columns_from_selected
        )
        self.results_frame.browser.setMinimumWidth(OUTPUT_WIDTH)
        self.study_frame.descriptive_panel.HomeButton.pressed.connect(
            self.home_button_handler
        )
        self.study_frame.home_panel.SaveReportButton.pressed.connect(self.save_handler)
        self.study_frame.descriptive_panel.checkBox_n.stateChanged.connect(
            self.process_descriptive
        )
        self.study_frame.descriptive_panel.checkBox_missing.stateChanged.connect(
            self.process_descriptive
        )
        self.study_frame.descriptive_panel.checkBox_mean.stateChanged.connect(
            self.process_descriptive
        )
        self.study_frame.descriptive_panel.checkBox_median.stateChanged.connect(
            self.process_descriptive
        )
        self.study_frame.descriptive_panel.checkBox_std.stateChanged.connect(
            self.process_descriptive
        )
        self.study_frame.descriptive_panel.checkBox_var.stateChanged.connect(
            self.process_descriptive
        )
        self.study_frame.descriptive_panel.checkBox_min.stateChanged.connect(
            self.process_descriptive
        )
        self.study_frame.descriptive_panel.checkBox_max.stateChanged.connect(
            self.process_descriptive
        )

        self.temp_file = None
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

    def add_columns_to_selected(self):
        w1 = self.study_frame.descriptive_panel.listWidget_all_columns.selectedItems()
        w1 = [c.text() for c in w1]
        selected = [
            self.study_frame.descriptive_panel.listWidget_selected_columns.item(
                i
            ).text()
            for i in range(
                self.study_frame.descriptive_panel.listWidget_selected_columns.count()
            )
        ]
        for item in w1:
            if item not in selected:
                self.study_frame.descriptive_panel.listWidget_selected_columns.addItems(
                    [item]
                )
        self.process_descriptive()

    def remove_columns_from_selected(self):
        for (
            item
        ) in (
            self.study_frame.descriptive_panel.listWidget_selected_columns.selectedItems()
        ):
            self.study_frame.descriptive_panel.listWidget_selected_columns.takeItem(
                self.study_frame.descriptive_panel.listWidget_selected_columns.row(item)
            )
        self.process_descriptive()

    def process_descriptive(self):
        logging.info("Running descriptive statistics")

        if self.current_index != DESCRIPTIVE_INDEX:
            logging.error("aborting: wrong index")
            return

        metadata = DescriptiveStudyMetadata(
            self.study_frame.descriptive_panel.get_metadata()
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
        self.results_frame.browser.load(
            QUrl.fromLocalFile(os.path.abspath(self.temp_file.name))
        )

        # set browser size
        sizes = self.splitter.sizes()
        if sizes[1] == 0:
            self.splitter.setSizes([sizes[0] - OUTPUT_WIDTH, OUTPUT_WIDTH, sizes[2]])
