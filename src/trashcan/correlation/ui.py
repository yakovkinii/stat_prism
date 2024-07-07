import logging
from typing import TYPE_CHECKING

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QFrame

from src.common import create_label
from src.common.column_selector.ui import ColumnSelector
from src.common.registry import NO_RESULT_SELECTED, data, data_selected, log_method, log_method_noarg, result_container
from src.core.descriptive.objects import DescriptiveStudyMetadata
from src.trashcan.common.home_delete_title.ui import HomeDeleteTitle
from src.trashcan.common.list_clickable.ui import CustomListWidget

# from models.correlation.core import run_correlation_study
from src.trashcan.correlation.core.main import run_correlation_study
from src.trashcan.correlation.objects import CorrelationStudyMetadata

if TYPE_CHECKING:
    from src.panels.study.ui import SettingsPanelClass


class Correlation:
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
        self.home_delete_title = HomeDeleteTitle(parent=self.frame, owner=self, title_text="Correlation Analysis")

        self.list_label = create_label(
            parent=self.frame,
            label_geometry=QtCore.QRect(10, 130, 381, 21),
            font_size=12,
            alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter,
        )

        self.list_widget = CustomListWidget(self.frame)
        self.list_widget.setGeometry(QtCore.QRect(10, 160, 381, 251))
        self.list_widget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

        self.list_widget.clicked.connect(self.invoke_column_selector)

        self.compact_checkbox = QtWidgets.QCheckBox(self.frame)
        self.compact_checkbox.setChecked(False)
        self.compact_checkbox.setGeometry(10, 430, 400, 50)
        self.compact_checkbox.stateChanged.connect(self.ui_changed)

        self.report_non_significant_checkbox = QtWidgets.QCheckBox(self.frame)
        self.report_non_significant_checkbox.setChecked(False)
        self.report_non_significant_checkbox.setGeometry(10, 470, 400, 50)
        self.report_non_significant_checkbox.stateChanged.connect(self.ui_changed)

        self.edit_table_title = QtWidgets.QLineEdit(self.frame)
        self.edit_table_title.setText("1")
        self.edit_table_title.setGeometry(80, 530, 30, 30)

        self.edit_table_title_label = QtWidgets.QLabel(self.frame)
        self.edit_table_title_label.setGeometry(10, 520, 85, 50)

        self.edit_filter = QtWidgets.QLineEdit(self.frame)
        self.edit_filter.setText("")
        self.edit_filter.setGeometry(80, 580, 200, 30)

        self.edit_filter_label = QtWidgets.QLabel(self.frame)
        self.edit_filter_label.setGeometry(10, 570, 85, 50)

        self.edit_table_title.editingFinished.connect(self.ui_changed)
        self.edit_filter.editingFinished.connect(self.ui_changed)

        self.state = self.state_selecting_columns
        self.selected_columns = []
        self.stackedWidget.setCurrentIndex(1)

        self.hold_run = False

    def retranslateUI(self):
        _translate = QtCore.QCoreApplication.translate
        self.home_delete_title.retranslateUI()
        self.compact_checkbox.setText(_translate("MainWindowClass", "Compact tabledata"))
        self.report_non_significant_checkbox.setText(
            _translate("MainWindowClass", "Report non-significant correlations")
        )
        self.list_label.setText(_translate("MainWindowClass", "Selected columns:"))
        self.edit_table_title_label.setText(_translate("MainWindowClass", "Table ID:"))
        self.edit_filter_label.setText(_translate("MainWindowClass", "Filter (df):"))

    @log_method
    def construct_metadata(self) -> CorrelationStudyMetadata:
        df = data._df
        try:
            data_selected._df = eval(str(self.edit_filter.text()))
            data_selected.filter = str(self.edit_filter.text())
        except Exception as e:
            logging.error(str(e))
            data_selected._df = data._df
            data_selected.filter = ""

        return CorrelationStudyMetadata(
            selected_columns=[self.list_widget.item(i).text() for i in range(self.list_widget.count())],
            compact=bool(self.compact_checkbox.checkState()),
            report_non_significant=bool(self.report_non_significant_checkbox.checkState()),
            table_name=self.edit_table_title.text(),
        )

    @log_method_noarg
    def ui_changed(self):
        if not self.hold_run:
            self.run()

    @log_method
    def run(self):
        metadata = self.construct_metadata()
        comment = data_selected.filter
        result_container.results[result_container.current_result] = run_correlation_study(
            df=data_selected._df, metadata=metadata, result_id=result_container.current_result, comment=comment
        )
        self.study_instance.mainwindow_instance.actionUpdateResultsFrame.trigger()

    @log_method
    def load_result(self):
        result = result_container.results[result_container.current_result]
        metadata: DescriptiveStudyMetadata = result.metadata
        self.load_metadata(metadata)

    @log_method
    def load_metadata(self, metadata):
        self.hold_run = True

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
    def home_button_handler(self):
        result_container.current_result = NO_RESULT_SELECTED
        self.study_instance.mainwindow_instance.actionUpdateStudyFrame.trigger()

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
