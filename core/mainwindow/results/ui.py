import logging
from typing import TYPE_CHECKING, Dict

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QTimer

from core.constants import NO_RESULT_SELECTED, OUTPUT_WIDTH
from core.mainwindow.results.result.ui import ResultWidget
from core.shared import result_container
from core.utility import log_method, log_method_noarg

if TYPE_CHECKING:
    from core.mainwindow.ui import MainWindow


class Results:
    @log_method
    def __init__(self, parent, mainwindow_instance):
        #   parent
        #       frame
        #           gridLayout
        #               scrollArea
        #                   scrollAreaWidgetContents
        #                       gridLayout_2
        #                           result_widgets
        self.vertical_spacer = None
        self.mainwindow_instance: MainWindow = mainwindow_instance

        self.frame = QtWidgets.QFrame(parent)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QtCore.QSize(OUTPUT_WIDTH, 0))
        # self.frame.setMaximumSize(QtCore.QSize(OUTPUT_WIDTH, 16777215))
        self.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QtWidgets.QScrollArea(self.frame)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.gridLayout_2 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)

        self.result_widgets: Dict[int, ResultWidget] = dict()

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea)

        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    def retranslateUI(self):
        pass

    @log_method_noarg
    def update(self):
        result_widgets_to_remove = set(self.result_widgets.keys()) - set(result_container.results.keys())
        result_widgets_to_add = set(result_container.results.keys()) - set(self.result_widgets.keys())
        result_widgets_to_update = set(result_container.results.keys()) - result_widgets_to_add

        for result_id in result_widgets_to_add:
            logging.info(f"Adding result {result_id} widget")
            result_widget = ResultWidget(
                self.scrollAreaWidgetContents, self, result_id, result_container.results[result_id]
            )
            self.result_widgets[result_id] = result_widget

        for result_id in result_widgets_to_update:
            logging.info(f"Updating result {result_id} widget")
            self.result_widgets[result_id].update(result_container.results[result_id])

        if len(result_widgets_to_add) != 0 or len(result_widgets_to_remove) != 0:
            logging.info("Recreating layout for all result widgets")
            # Clear layout
            for i in range(self.gridLayout_2.count()):
                self.gridLayout_2.takeAt(0)

            for result_id in result_widgets_to_remove:
                logging.info(f"Removing result {result_id} widget")
                self.result_widgets[result_id].frame.deleteLater()
                del self.result_widgets[result_id]

            last_result_id = None
            for result_id, result in result_container.results.items():
                self.gridLayout_2.addWidget(self.result_widgets[result_id].frame)
                self.result_widgets[result_id].frame.setSizePolicy(
                    QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum
                )
                last_result_id = result_id
            if last_result_id is not None:
                self.result_widgets[last_result_id].frame.setSizePolicy(
                    QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
                )

        for result_id, result_widget in self.result_widgets.items():
            if result_id == result_container.current_result:
                result_widget.frame.setStyleSheet("background-color: #fff;")
            else:
                result_widget.frame.setStyleSheet("background-color: #fafafa;")

        if result_container.current_result is not NO_RESULT_SELECTED:
            self.timer = QTimer()
            self.timer.timeout.connect(self.ensure_visible)
            self.timer.setSingleShot(True)
            self.timer.start(10)

    def ensure_visible(self):
        if result_container.current_result is not NO_RESULT_SELECTED:
            self.scrollArea.ensureWidgetVisible(self.result_widgets[result_container.current_result].frame)
