from PyQt5 import QtCore, QtWidgets

from objects.metadata import DescriptiveStudyMetadataUI
from ui.constructors.misc import add_checkbox_to_groupbox, create_tool_button


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
