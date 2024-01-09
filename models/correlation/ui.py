from typing import TYPE_CHECKING

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QFrame

from core.common_ui import create_label
from core.constants import NO_RESULT_SELECTED
from core.shared import data, result_container
from core.utility import log_method, log_method_noarg
from models.common.column_selector.ui import ColumnSelector
from models.common.home_delete_title.ui import HomeDeleteTitle
from models.common.list_clickable.ui import CustomListWidget
from models.correlation.core import run_correlation_study
from models.correlation.objects import CorrelationStudyMetadata
from models.descriptive.objects import DescriptiveStudyMetadata

if TYPE_CHECKING:
    from core.mainwindow.study.ui import Study


class Correlation:
    def __init__(self, study_instance):
        self.state_ready = 0
        self.state_selecting_columns = 1

        self.study_instance: Study = study_instance
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
        self.home_delete_title = HomeDeleteTitle(parent=self.frame, owner=self, title_text="Correlation\nAnalysis")

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

        self.state = self.state_selecting_columns
        self.selected_columns = []
        self.stackedWidget.setCurrentIndex(1)

        self.hold_run = False

    def retranslateUI(self):
        _translate = QtCore.QCoreApplication.translate
        self.home_delete_title.retranslateUI()

        self.list_label.setText(_translate("MainWindow", "Selected columns:"))

    @log_method
    def construct_metadata(self) -> CorrelationStudyMetadata:
        return CorrelationStudyMetadata(
            selected_columns=[self.list_widget.item(i).text() for i in range(self.list_widget.count())]
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
            columns=list(data.df.columns),
            dtypes=data.df.dtypes.astype(str).tolist(),
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
