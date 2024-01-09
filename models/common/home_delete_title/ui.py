from PyQt5 import QtCore
from PyQt5.QtWidgets import QFrame

from core.common_ui import create_label, create_tool_button_qta
from core.constants import NO_RESULT_SELECTED
from core.shared import result_container
from core.utility import log_method


class HomeDeleteTitle:
    @log_method
    def __init__(self, parent, owner, title_text):
        self.title_text = title_text
        self.owner = owner
        self.frame = QFrame(parent)
        self.HomeButton = create_tool_button_qta(
            parent=self.frame,
            button_geometry=QtCore.QRect(10, 10, 61, 61),
            icon_path="fa.home",
            icon_size=QtCore.QSize(40, 40),
        )

        self.DeleteButton = create_tool_button_qta(
            parent=self.frame,
            button_geometry=QtCore.QRect(10 + 380 - 59, 10, 61, 61),
            icon_path="mdi.delete-forever",
            icon_size=QtCore.QSize(40, 40),
        )

        self.title = create_label(
            parent=self.frame,
            label_geometry=QtCore.QRect(10 + 61, 0, 381 - 122, 81),
            font_size=16,
            alignment=QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter,
        )

        self.HomeButton.pressed.connect(self.home_button_handler)
        self.DeleteButton.pressed.connect(self.delete_button_handler)

    def retranslateUI(self):
        _translate = QtCore.QCoreApplication.translate
        self.title.setText(_translate("MainWindow", self.title_text))

    @log_method
    def home_button_handler(self):
        result_container.current_result = NO_RESULT_SELECTED
        self.owner.study_instance.mainwindow_instance.actionUpdateStudyFrame.trigger()

    @log_method
    def delete_button_handler(self):
        del result_container.results[result_container.current_result]
        result_container.current_result = NO_RESULT_SELECTED
        self.owner.study_instance.mainwindow_instance.actionUpdateStudyFrame.trigger()
        self.owner.study_instance.mainwindow_instance.actionUpdateResultsFrame.trigger()
