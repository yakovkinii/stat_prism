import logging

from PyQt5 import QtCore, QtWidgets

from core.misc import get_html_start_end
from modules.descriptive.core import run_descriptive_study
from modules.descriptive.metadata import DescriptiveStudyMetadataUI, DescriptiveStudyMetadata
from core.ui.misc import add_checkbox_to_groupbox, create_tool_button


class Descriptive:
    def __init__(self):
        self.widget = QtWidgets.QWidget()

        self.listWidget_all_columns = QtWidgets.QListWidget(self.widget)
        self.listWidget_all_columns.setGeometry(QtCore.QRect(10, 93, 381, 271))
        self.listWidget_all_columns.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )

        self.listWidget_selected_columns = QtWidgets.QListWidget(self.widget)
        self.listWidget_selected_columns.setGeometry(QtCore.QRect(10, 423, 381, 231))
        self.listWidget_selected_columns.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )

        self.groupBox = QtWidgets.QGroupBox(self.widget)
        self.groupBox.setGeometry(QtCore.QRect(10, 663, 116, 251))
        self.formLayout = QtWidgets.QFormLayout(self.groupBox)

        self.checkBox_n = add_checkbox_to_groupbox(self.groupBox, 0, self.formLayout)
        self.checkBox_missing = add_checkbox_to_groupbox(
            self.groupBox, 1, self.formLayout
        )
        self.checkBox_mean = add_checkbox_to_groupbox(self.groupBox, 2, self.formLayout)
        self.checkBox_median = add_checkbox_to_groupbox(
            self.groupBox, 3, self.formLayout
        )
        self.checkBox_std = add_checkbox_to_groupbox(self.groupBox, 4, self.formLayout)
        self.checkBox_var = add_checkbox_to_groupbox(self.groupBox, 5, self.formLayout)
        self.checkBox_min = add_checkbox_to_groupbox(self.groupBox, 6, self.formLayout)
        self.checkBox_max = add_checkbox_to_groupbox(self.groupBox, 7, self.formLayout)

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

        self.DownButton.pressed.connect(
            self.add_columns_to_selected
        )
        self.UpButton.pressed.connect(
            self.remove_columns_from_selected
        )

        # Trigger updates on change
        self.actionTriggerUpdate = QtWidgets.QAction(self.widget)
        self.checkBox_n.stateChanged.connect(self.actionTriggerUpdate.trigger)
        self.checkBox_missing.stateChanged.connect(self.actionTriggerUpdate.trigger)
        self.checkBox_mean.stateChanged.connect(self.actionTriggerUpdate.trigger)
        self.checkBox_median.stateChanged.connect(self.actionTriggerUpdate.trigger)
        self.checkBox_std.stateChanged.connect(self.actionTriggerUpdate.trigger)
        self.checkBox_var.stateChanged.connect(self.actionTriggerUpdate.trigger)
        self.checkBox_min.stateChanged.connect(self.actionTriggerUpdate.trigger)
        self.checkBox_max.stateChanged.connect(self.actionTriggerUpdate.trigger)
        # self.DownButton.pressed.connect(self.actionTriggerUpdate.trigger)
        # self.UpButton.pressed.connect(self.actionTriggerUpdate.trigger)

    def retranslateUI(self):
        _translate = QtCore.QCoreApplication.translate
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

    def get_metadata(self) -> DescriptiveStudyMetadataUI:
        return DescriptiveStudyMetadataUI(
            selected_columns=[
                self.listWidget_selected_columns.item(i).text()
                for i in range(self.listWidget_selected_columns.count())
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

    def process_descriptive(self, df):
        logging.info("Running descriptive statistics")

        metadata = DescriptiveStudyMetadata(
            self.get_metadata()
        )
        html_start, html_end = get_html_start_end()
        return html_start + run_descriptive_study(df, metadata) + html_end

    def add_columns_to_selected(self):
        w1 = self.listWidget_all_columns.selectedItems()
        w1 = [c.text() for c in w1]
        selected = [
            self.listWidget_selected_columns.item(
                i
            ).text()
            for i in range(
                self.listWidget_selected_columns.count()
            )
        ]
        for item in w1:
            if item not in selected:
                self.listWidget_selected_columns.addItems(
                    [item]
                )
        self.actionTriggerUpdate.trigger()

    def remove_columns_from_selected(self):
        for (
            item
        ) in (
            self.listWidget_selected_columns.selectedItems()
        ):
            self.listWidget_selected_columns.takeItem(
                self.listWidget_selected_columns.row(item)
            )
        self.actionTriggerUpdate.trigger()
