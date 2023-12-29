from PyQt5 import QtCore, QtWidgets

from core.ui.common import create_label, create_tool_button


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

        self.DescriptiveStatisticsButton_literal = create_tool_button(
            parent=self.widget,
            button_geometry=QtCore.QRect(240, 240, 101, 101),
            icon_path=":/mat/resources/material-icons-png-master/png/black/bar_chart/round-4x.png",
            icon_size=QtCore.QSize(60, 60),
        )
        self.DescriptiveStatisticsButton_literal.setEnabled(False)

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

        self.label_discriptive_literal = create_label(
            parent=self.widget,
            label_geometry=QtCore.QRect(240, 350, 101, 71),
            font_size=10,
            alignment=QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop,
        )

    def retranslateUI(self):
        _translate = QtCore.QCoreApplication.translate

        self.DescriptiveStatisticsButton.setText(
            _translate("MainWindow", "Descriptive\n" "Statistics")
        )
        self.label_open.setText(_translate("MainWindow", "Open File"))
        self.label_discriptive.setText(
            _translate("MainWindow", "Descriptive\n" "Statistics\n" "(Numeric)")
        )
        self.DescriptiveStatisticsButton_literal.setText(
            _translate("MainWindow", "Descriptive\n" "Statistics")
        )
        self.label_discriptive_literal.setText(
            _translate("MainWindow", "Descriptive\n" "Statistics\n" "(Literal)")
        )
        self.label_save.setText(_translate("MainWindow", "Save Report"))
