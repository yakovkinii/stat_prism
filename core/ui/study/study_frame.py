from PyQt5 import QtCore, QtWidgets

from core.ui.study.home_panel import Home
from modules.descriptive.ui import Descriptive


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

        self.home_panel = Home()
        self.descriptive_panel = Descriptive()

        self.stackedWidget.addWidget(self.home_panel.widget)
        self.stackedWidget.addWidget(self.descriptive_panel.widget)

        self.gridLayout.addWidget(self.stackedWidget, 0, 0, 1, 1)

    def retranslateUI(self):
        self.home_panel.retranslateUI()
        self.descriptive_panel.retranslateUI()
