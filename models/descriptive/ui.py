from typing import TYPE_CHECKING

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QFrame

from core.common_ui import add_checkbox_to_groupbox, create_tool_button, create_tool_button_qta, create_label
from core.constants import NO_RESULT_SELECTED
from core.shared import data, result_container
from core.utility import log_method, log_method_noarg
from models.descriptive.core import run_descriptive_study
from models.descriptive.objects import DescriptiveStudyMetadata

if TYPE_CHECKING:
    from core.mainwindow.study.ui import Study


class Descriptive:
    def __init__(self, study_instance):
        self.study_instance: Study = study_instance
        self.widget = QtWidgets.QWidget()

        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget = QtWidgets.QStackedWidget(self.widget)

        self.frame = QFrame(self.widget)

        # === MODELS GO HERE ===
        self.descriptive_panel: Descriptive = Descriptive(self)
        self.correlation_panel: Correlation = Correlation(self)

        # =======================

        self.stackedWidget.addWidget(self.home_panel.widget)
        self.stackedWidget.addWidget(self.descriptive_panel.widget)
        self.stackedWidget.addWidget(self.correlation_panel.widget)

        self.gridLayout.addWidget(self.stackedWidget, 0, 0, 1, 1)
        self.stackedWidget.setCurrentIndex(0)




        self.groupBox = QtWidgets.QGroupBox(self.widget)
        self.groupBox.setGeometry(QtCore.QRect(10, 663, 116, 251))
        self.formLayout = QtWidgets.QFormLayout(self.groupBox)

        self.checkBox_n = add_checkbox_to_groupbox(self.groupBox, 0, self.formLayout)
        self.checkBox_missing = add_checkbox_to_groupbox(self.groupBox, 1, self.formLayout)
        self.checkBox_mean = add_checkbox_to_groupbox(self.groupBox, 2, self.formLayout)
        self.checkBox_median = add_checkbox_to_groupbox(self.groupBox, 3, self.formLayout)
        self.checkBox_std = add_checkbox_to_groupbox(self.groupBox, 4, self.formLayout)
        self.checkBox_var = add_checkbox_to_groupbox(self.groupBox, 5, self.formLayout)
        self.checkBox_min = add_checkbox_to_groupbox(self.groupBox, 6, self.formLayout)
        self.checkBox_max = add_checkbox_to_groupbox(self.groupBox, 7, self.formLayout)

        self.HomeButton = create_tool_button_qta(
            parent=self.widget,
            button_geometry=QtCore.QRect(10, 10, 61, 61),
            icon_path="fa.home",
            icon_size=QtCore.QSize(40, 40),
        )

        self.DeleteButton = create_tool_button_qta(
            parent=self.widget,
            button_geometry=QtCore.QRect(10+380-59, 10, 61, 61),
            icon_path="mdi.delete-forever",
            icon_size=QtCore.QSize(40, 40),
        )
        self.DeleteButton.setEnabled(False)

        self.title = create_label(
            parent=self.widget,
            label_geometry=QtCore.QRect(10+61,10, 381-122, 61),
            font_size=16,
            alignment=QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter,
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

        # Trigger updates on change
        self.checkBox_n.stateChanged.connect(self.ui_changed)
        self.checkBox_missing.stateChanged.connect(self.ui_changed)
        self.checkBox_mean.stateChanged.connect(self.ui_changed)
        self.checkBox_median.stateChanged.connect(self.ui_changed)
        self.checkBox_std.stateChanged.connect(self.ui_changed)
        self.checkBox_var.stateChanged.connect(self.ui_changed)
        self.checkBox_min.stateChanged.connect(self.ui_changed)
        self.checkBox_max.stateChanged.connect(self.ui_changed)

        self.HomeButton.pressed.connect(self.home_button_handler)

        self.hold_run = False

    def retranslateUI(self):
        _translate = QtCore.QCoreApplication.translate
        self.title.setText(_translate("MainWindow", "Descriptive\nStatistics"))
        self.groupBox.setTitle(_translate("MainWindow", "Options"))
        self.checkBox_n.setText(_translate("MainWindow", "N"))
        self.checkBox_missing.setText(_translate("MainWindow", "Missing"))
        self.checkBox_mean.setText(_translate("MainWindow", "Mean"))
        self.checkBox_median.setText(_translate("MainWindow", "Median"))
        self.checkBox_std.setText(_translate("MainWindow", "Std. deviation"))
        self.checkBox_var.setText(_translate("MainWindow", "Variance"))
        self.checkBox_min.setText(_translate("MainWindow", "Minimum"))
        self.checkBox_max.setText(_translate("MainWindow", "Maximum"))
        self.HomeButton.setShortcut(_translate("MainWindow", "Backspace"))

    @log_method
    def construct_metadata(self) -> DescriptiveStudyMetadata:
        return DescriptiveStudyMetadata(
            selected_columns=[
                self.listWidget_selected_columns.item(i).text() for i in range(self.listWidget_selected_columns.count())
            ],
            n=bool(self.checkBox_n.checkState()),
            missing=bool(self.checkBox_missing.checkState()),
            mean=bool(self.checkBox_mean.checkState()),
            median=bool(self.checkBox_median.checkState()),
            stddev=bool(self.checkBox_std.checkState()),
            variance=bool(self.checkBox_var.checkState()),
            minimum=bool(self.checkBox_min.checkState()),
            maximum=bool(self.checkBox_max.checkState()),
        )

    @log_method_noarg
    def ui_changed(self):
        if not self.hold_run:
            self.run()

    @log_method
    def run(self):
        metadata = self.construct_metadata()
        result_container.results[result_container.current_result] = run_descriptive_study(
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

        self.checkBox_n.setChecked(metadata.n)
        self.checkBox_missing.setChecked(metadata.missing)
        self.checkBox_mean.setChecked(metadata.mean)
        self.checkBox_median.setChecked(metadata.median)
        self.checkBox_std.setChecked(metadata.stddev)
        self.checkBox_var.setChecked(metadata.variance)
        self.checkBox_min.setChecked(metadata.minimum)
        self.checkBox_max.setChecked(metadata.maximum)

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
