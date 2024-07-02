from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

from src.common.ui_constructor import VerticalLayout
from src.results_panel.result.common.label import LabelClickable
from src.common.objects import TextResultItem
from src.common.registry import log_method


class TextResultItemWidget:
    @log_method
    def __init__(self, parent, result_widget_instance, item: TextResultItem):
        self.result_widget_instance = result_widget_instance
        self.item: TextResultItem = item

        self.frame = QtWidgets.QFrame(parent)

        self.layout = VerticalLayout(self.frame, padding_left=20, padding_right=20)

        self.label = LabelClickable(self.frame)
        self.label.setWordWrap(True)
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.label.setAlignment(QtCore.Qt.AlignJustify)
        font = QtGui.QFont("Segoe UI")
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setText(item.text)
        self.layout.addWidget(self.label)
