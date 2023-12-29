import logging

import pandas as pd
from PyQt5 import QtCore, QtWidgets

from core.common_ui import create_label, create_tool_button
from core.constants import DESCRIPTIVE_MODEL_NAME, NO_RESULT_SELECTED
from core.objects import Result
from core.shared import data, result_container
from core.utility import get_next_valid_result_id, select_result


class Home:
    def __init__(self):
        self.widget = QtWidgets.QWidget()

        self.DescriptiveStatisticsButton = create_tool_button(
            parent=self.widget,
            button_geometry=QtCore.QRect(60, 240, 101, 101),
            icon_path=":/mat/resources/material-icons-png-master/png/black/bar_chart/round-4x.png",
            icon_size=QtCore.QSize(60, 60),
        )

        self.OpenFileButton = create_tool_button(
            parent=self.widget,
            button_geometry=QtCore.QRect(60, 40, 101, 101),
            icon_path=":/mat/resources/material-icons-png-master/png/black/folder_open/round-4x.png",
            icon_size=QtCore.QSize(60, 60),
        )

        # self.DescriptiveStatisticsButton_literal = create_tool_button(
        #     parent=self.widget,
        #     button_geometry=QtCore.QRect(240, 240, 101, 101),
        #     icon_path=":/mat/resources/material-icons-png-master/png/black/bar_chart/round-4x.png",
        #     icon_size=QtCore.QSize(60, 60),
        # )
        # self.DescriptiveStatisticsButton_literal.setEnabled(False)

        self.SaveReportButton = create_tool_button(
            parent=self.widget,
            button_geometry=QtCore.QRect(240, 40, 101, 101),
            icon_path=":/mat/resources/material-icons-png-master/png/black/save_alt/round-4x.png",
            icon_size=QtCore.QSize(60, 60),
        )

        self.label_open = create_label(
            parent=self.widget,
            label_geometry=QtCore.QRect(60, 150, 101, 61),
            font_size=10,
            alignment=QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop,
        )

        self.label_discriptive = create_label(
            parent=self.widget,
            label_geometry=QtCore.QRect(60, 350, 101, 71),
            font_size=10,
            alignment=QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop,
        )
        self.label_save = create_label(
            parent=self.widget,
            label_geometry=QtCore.QRect(240, 150, 101, 61),
            font_size=10,
            alignment=QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop,
        )

        # self.label_discriptive_literal = create_label(
        #     parent=self.widget,
        #     label_geometry=QtCore.QRect(240, 350, 101, 71),
        #     font_size=10,
        #     alignment=QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop,
        # )

        self.OpenFileButton.pressed.connect(self.open_handler)
        self.DescriptiveStatisticsButton.pressed.connect(self.create_descriptive)
        self.actionUpdateStudyFrame = QtWidgets.QAction(self.widget)
        self.actionUpdateTableFrame = QtWidgets.QAction(self.widget)
        # self.SaveReportButton.pressed.connect(self.save_handler)

    def retranslateUI(self):
        _translate = QtCore.QCoreApplication.translate

        self.DescriptiveStatisticsButton.setText(
            _translate("MainWindow", "Descriptive\n" "Statistics")
        )
        self.label_open.setText(_translate("MainWindow", "Open File"))
        self.label_discriptive.setText(
            _translate("MainWindow", "Descriptive\n" "Statistics\n" "(Numeric)")
        )
        # self.DescriptiveStatisticsButton_literal.setText(
        #     _translate("MainWindow", "Descriptive\n" "Statistics")
        # )
        # self.label_discriptive_literal.setText(
        #     _translate("MainWindow", "Descriptive\n" "Statistics\n" "(Literal)")
        # )
        self.label_save.setText(_translate("MainWindow", "Save Report"))

    def create_descriptive(self):
        result_id = get_next_valid_result_id()
        result_container.results[result_id] = Result(
            result_id=result_id, module_name=DESCRIPTIVE_MODEL_NAME
        )
        select_result(result_id)
        self.actionUpdateStudyFrame.trigger()

    def home_button_handler(self):
        select_result(NO_RESULT_SELECTED)
        self.actionUpdateStudyFrame.trigger()

    # def save_handler(self):
    #     options = QFileDialog.Options()
    #     file_path, _ = QFileDialog.getSaveFileName(
    #         self, "Save File", "", "HTML Files (*.html);;All Files (*)", options=options
    #     )
    #
    #     if file_path:
    #         # If the user doesn't add the .html extension, add it for them
    #         if not file_path.lower().endswith(".html"):
    #             file_path += ".html"
    #         with open(file_path, "wt") as f:
    #             f.write(self.output)
    #     self.study_frame.home_panel.SaveReportButton.setDown(False)

    def open_handler(self):
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.widget,
            "Open CSV File",
            "",
            "Excel Files (*.xlsx *.csv);;All Files (*)",
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

        if data.df is not None:
            self.actionUpdateTableFrame.trigger()

            select_result(NO_RESULT_SELECTED)
            self.actionUpdateStudyFrame.trigger()
            self.OpenFileButton.setDown(False)
