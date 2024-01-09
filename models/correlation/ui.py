from typing import TYPE_CHECKING

from PyQt5 import QtCore, QtWidgets

from core.common_ui import create_tool_button
from core.constants import NO_RESULT_SELECTED
from core.shared import data, result_container
from core.utility import log_method, log_method_noarg
from models.correlation.core import run_correlation_study
from models.correlation.objects import CorrelationStudyMetadata
from models.descriptive.objects import DescriptiveStudyMetadata

if TYPE_CHECKING:
    from core.mainwindow.study.ui import Study


class Correlation:
    def __init__(self, study_instance):
        self.study_instance: Study = study_instance
        self.widget = QtWidgets.QWidget()

        self.listWidget_all_columns = QtWidgets.QListWidget(self.widget)
        self.listWidget_all_columns.setGeometry(QtCore.QRect(10, 93, 381, 271))
        self.listWidget_all_columns.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.listWidget_selected_columns = QtWidgets.QListWidget(self.widget)
        self.listWidget_selected_columns.setGeometry(QtCore.QRect(10, 423, 381, 231))
        self.listWidget_selected_columns.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.HomeButton = create_tool_button(
            parent=self.widget,
            button_geometry=QtCore.QRect(10, 10, 61, 61),
            icon_path=":/mat/resources/material-icons-png-master/png/black/menu/round-4x.png",
            icon_size=QtCore.QSize(40, 40),
        )

        self.DownButton = create_tool_button(
            parent=self.widget,
            button_geometry=QtCore.QRect(140, 370, 51, 51),
            icon_path=":/mat/resources/material-icons-png-master/png/black/arrow_downward/round-4x.png",
            icon_size=QtCore.QSize(40, 40),
        )

        self.UpButton = create_tool_button(
            parent=self.widget,
            button_geometry=QtCore.QRect(210, 370, 51, 51),
            icon_path=":/mat/resources/material-icons-png-master/png/black/arrow_upward/round-4x.png",
            icon_size=QtCore.QSize(40, 40),
        )

        self.DownButton.pressed.connect(self.add_columns_to_selected)
        self.UpButton.pressed.connect(self.remove_columns_from_selected)

        self.HomeButton.pressed.connect(self.home_button_handler)

        self.hold_run = False

    def retranslateUI(self):
        _translate = QtCore.QCoreApplication.translate
        self.HomeButton.setShortcut(_translate("MainWindow", "Backspace"))

    @log_method
    def construct_metadata(self) -> CorrelationStudyMetadata:
        return CorrelationStudyMetadata(
            selected_columns=[
                self.listWidget_selected_columns.item(i).text() for i in range(self.listWidget_selected_columns.count())
            ]
        )

    @log_method_noarg
    def ui_changed(self):
        if not self.hold_run:
            self.run()

    @log_method
    def run(self):
        metadata = self.construct_metadata()
        result_container.results[result_container.current_result] = run_correlation_study(
            df=data.df, metadata=metadata, result_id=result_container.current_result
        )
        self.study_instance.mainwindow_instance.actionUpdateResultsFrame.trigger()

    @log_method
    def add_columns_to_selected(self):
        w1 = self.listWidget_all_columns.selectedItems()
        w1 = [c.text() for c in w1]
        selected = [
            self.listWidget_selected_columns.item(i).text() for i in range(self.listWidget_selected_columns.count())
        ]
        for item in w1:
            if item not in selected:
                self.listWidget_selected_columns.addItems([item])
        self.listWidget_selected_columns.clearSelection()
        self.listWidget_all_columns.clearSelection()
        self.ui_changed()

    @log_method
    def remove_columns_from_selected(self):
        for item in self.listWidget_selected_columns.selectedItems():
            self.listWidget_selected_columns.takeItem(self.listWidget_selected_columns.row(item))
        self.listWidget_selected_columns.clearSelection()
        self.listWidget_all_columns.clearSelection()
        self.ui_changed()

    @log_method
    def load_result(self):
        result = result_container.results[result_container.current_result]
        metadata: DescriptiveStudyMetadata = result.metadata
        self.load_metadata(metadata)

    @log_method
    def load_metadata(self, metadata):
        self.hold_run = True

        # update selection list
        self.listWidget_all_columns.clear()
        self.listWidget_selected_columns.clear()
        for column in data.df.columns:
            if data.df[column].dtype.kind in "biufc":  # numeric
                if column in metadata.selected_columns:
                    self.listWidget_selected_columns.addItem(column)
                else:
                    self.listWidget_all_columns.addItem(column)

        self.hold_run = False

    @log_method
    def home_button_handler(self):
        result_container.current_result = NO_RESULT_SELECTED
        self.study_instance.mainwindow_instance.actionUpdateStudyFrame.trigger()
