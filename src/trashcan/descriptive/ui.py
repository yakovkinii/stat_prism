from typing import TYPE_CHECKING

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QFrame

from src.common import add_checkbox_to_groupbox, create_label
from src.common.column_selector.ui import ColumnSelector
from src.common.registry import data, log_method, log_method_noarg, result_container
from src.core.descriptive.core import run_descriptive_study
from src.core.descriptive.objects import DescriptiveStudyMetadata
from src.trashcan.common.home_delete_title.ui import HomeDeleteTitle
from src.trashcan.common.list_clickable.ui import CustomListWidget

if TYPE_CHECKING:
    from src.panels.study.ui import SettingsPanelClass


class Descriptive:
    def __init__(self, study_instance):
        self.state_ready = 0
        self.state_selecting_columns = 1

        self.study_instance: SettingsPanelClass = study_instance
        self.widget = QtWidgets.QWidget()

        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget = QtWidgets.QStackedWidget(self.widget)

        self.frame = QFrame(self.widget)
        self.column_selector = ColumnSelector(parent=self.widget, owner=self)

        self.stackedWidget.addWidget(self.frame)
        self.stackedWidget.addWidget(self.column_selector.frame)

        self.gridLayout.addWidget(self.stackedWidget, 0, 0, 1, 1)

        # Populate main frame
        self.home_delete_title = HomeDeleteTitle(parent=self.frame, owner=self, title_text="Descriptive\nStatistics")

        self.list_label = create_label(
            parent=self.frame,
            label_geometry=QtCore.QRect(10, 100, 381, 21),
            font_size=12,
            alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter,
        )

        self.list_widget = CustomListWidget(self.frame)
        self.list_widget.setGeometry(QtCore.QRect(10, 130, 381, 251))
        self.list_widget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

        self.list_widget.clicked.connect(self.invoke_column_selector)

        self.groupBox = QtWidgets.QGroupBox(self.frame)
        self.groupBox.setVisible(False)
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

        # Trigger updates on change
        self.checkBox_n.stateChanged.connect(self.ui_changed)
        self.checkBox_missing.stateChanged.connect(self.ui_changed)
        self.checkBox_mean.stateChanged.connect(self.ui_changed)
        self.checkBox_median.stateChanged.connect(self.ui_changed)
        self.checkBox_std.stateChanged.connect(self.ui_changed)
        self.checkBox_var.stateChanged.connect(self.ui_changed)
        self.checkBox_min.stateChanged.connect(self.ui_changed)
        self.checkBox_max.stateChanged.connect(self.ui_changed)

        self.checkBox_n.setEnabled(False)
        self.checkBox_missing.setEnabled(False)
        self.checkBox_mean.setEnabled(False)
        self.checkBox_median.setEnabled(False)
        self.checkBox_std.setEnabled(False)
        self.checkBox_var.setEnabled(False)
        self.checkBox_min.setEnabled(False)
        self.checkBox_max.setEnabled(False)

        self.state = self.state_selecting_columns
        self.selected_columns = []
        self.stackedWidget.setCurrentIndex(1)

        self.hold_run = False

    def retranslateUI(self):
        _translate = QtCore.QCoreApplication.translate
        self.home_delete_title.retranslateUI()
        self.list_label.setText(_translate("MainWindowClass", "Selected columns:"))
        self.groupBox.setTitle(_translate("MainWindowClass", "Options"))
        self.checkBox_n.setText(_translate("MainWindowClass", "N"))
        self.checkBox_missing.setText(_translate("MainWindowClass", "Missing"))
        self.checkBox_mean.setText(_translate("MainWindowClass", "Mean"))
        self.checkBox_median.setText(_translate("MainWindowClass", "Median"))
        self.checkBox_std.setText(_translate("MainWindowClass", "Std. deviation"))
        self.checkBox_var.setText(_translate("MainWindowClass", "Variance"))
        self.checkBox_min.setText(_translate("MainWindowClass", "Minimum"))
        self.checkBox_max.setText(_translate("MainWindowClass", "Maximum"))

    @log_method
    def construct_metadata(self) -> DescriptiveStudyMetadata:
        return DescriptiveStudyMetadata(
            selected_columns=[self.list_widget.item(i).text() for i in range(self.list_widget.count())],
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
            df=data._df, metadata=metadata, result_id=result_container.current_result
        )
        self.study_instance.mainwindow_instance.actionUpdateResultsFrame.trigger()

    @log_method
    def load_result(self):
        result = result_container.results[result_container.current_result]
        metadata: DescriptiveStudyMetadata = result.metadata
        self.load_metadata(metadata)

    @log_method
    def load_metadata(self, metadata: DescriptiveStudyMetadata):
        self.hold_run = True

        self.checkBox_n.setChecked(metadata.n)
        self.checkBox_missing.setChecked(metadata.missing)
        self.checkBox_mean.setChecked(metadata.mean)
        self.checkBox_median.setChecked(metadata.median)
        self.checkBox_std.setChecked(metadata.stddev)
        self.checkBox_var.setChecked(metadata.variance)
        self.checkBox_min.setChecked(metadata.minimum)
        self.checkBox_max.setChecked(metadata.maximum)

        if len(metadata.selected_columns) == 0:
            self.state = self.state_selecting_columns
            self.selected_columns = []
            self.invoke_column_selector()
        else:
            self.selected_columns = metadata.selected_columns
            self.list_widget.clear()
            for column in self.selected_columns:
                self.list_widget.addItem(column)

        self.hold_run = False

    @log_method
    def invoke_column_selector(self):
        self.column_selector.configure(
            columns=list(data._df.columns),
            dtypes=data._df.dtypes.astype(str).tolist(),
            selected_columns=self.selected_columns,
            allowed_dtypes=["int64", "float64"],
        )
        self.state = self.state_selecting_columns
        self.stackedWidget.setCurrentIndex(1)

    @log_method
    def column_selector_accept(self, selected_columns):
        self.state = self.state_ready
        self.selected_columns = selected_columns

        self.list_widget.clear()
        for column in selected_columns:
            self.list_widget.addItem(column)

        self.stackedWidget.setCurrentIndex(0)
        self.ui_changed()

    @log_method
    def column_selector_cancel(self):
        self.state = self.state_ready
        self.stackedWidget.setCurrentIndex(0)
