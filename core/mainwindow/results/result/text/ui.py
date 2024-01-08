from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

from core.mainwindow.results.result.common.label import LabelClickable
from core.mainwindow.results.result.common.title import TitleWidget
from core.objects import TextResultItem
from core.utility import log_method


class TextResultItemWidget:
    @log_method
    def __init__(self, parent, result_widget_instance, item: TextResultItem):
        self.result_widget_instance = result_widget_instance
        self.item: TextResultItem = item

        self.frame = QtWidgets.QFrame(parent)
        self.frame.setAttribute(Qt.WA_StyledBackground, True)
        self.title_widget = TitleWidget(self.frame, self.item.title)

        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setContentsMargins(20, 0, 20, 0)
        self.gridLayout.addWidget(self.title_widget)

        self.label = LabelClickable(self.frame)
        self.label.setWordWrap(True)
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.label.setAlignment(QtCore.Qt.AlignJustify)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setText(item.text)

        self.gridLayout.addWidget(self.label)
