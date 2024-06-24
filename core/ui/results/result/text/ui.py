from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

from core.ui.common.common_ui.layout import VerticalLayout
from core.ui.results.result.common.label import LabelClickable
from core.registry.objects import TextResultItem
from core.registry.utility import log_method


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
