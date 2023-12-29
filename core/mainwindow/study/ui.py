from typing import Dict

from PyQt5 import QtCore, QtWidgets

from core.constants import DESCRIPTIVE_MODEL_NAME, NO_RESULT_SELECTED
from core.mainwindow.study.home.ui import Home
from core.objects import ModelRegistryItem
from core.shared import result_container
from models.descriptive.ui import Descriptive


class Study:
    def __init__(self, parent):
        #   parent
        #       frame
        #           gridLayout
        #               stackedWidget
        #                   home_panel
        #                   descriptive_panel

        self.frame = QtWidgets.QFrame(parent)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QtCore.QSize(410, 0))
        self.frame.setMaximumSize(QtCore.QSize(410, 16777215))
        self.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)

        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget = QtWidgets.QStackedWidget(self.frame)

        self.home_panel: Home = Home()

        # === MODELS GO HERE ===
        self.descriptive_panel: Descriptive = Descriptive()

        # =======================

        self.stackedWidget.addWidget(self.home_panel.widget)
        self.stackedWidget.addWidget(self.descriptive_panel.widget)

        self.gridLayout.addWidget(self.stackedWidget, 0, 0, 1, 1)
        self.stackedWidget.setCurrentIndex(0)
        self.home_panel.actionUpdateStudyFrame.triggered.connect(self.update)

        # MODEL REGISTRY
        self.registry: Dict[str, ModelRegistryItem] = {
            DESCRIPTIVE_MODEL_NAME: ModelRegistryItem(
                model_name=DESCRIPTIVE_MODEL_NAME,
                stacked_widget_index=1,
                setup_from_result_handler=self.descriptive_panel.setup_from_result,
                run_handler=self.descriptive_panel.run,
            )
        }

    def retranslateUI(self):
        self.home_panel.retranslateUI()
        self.descriptive_panel.retranslateUI()

    def update(self):
        result_id = result_container.current_result
        if result_id == NO_RESULT_SELECTED:
            self.stackedWidget.setCurrentIndex(0)
            return

        model_name = result_container.results[result_id].module_name
        self.stackedWidget.setCurrentIndex(
            self.registry[model_name].stacked_widget_index
        )

        if result_id != NO_RESULT_SELECTED:
            self.registry[model_name].from_result_handler()
            self.registry[model_name].update_handler()
