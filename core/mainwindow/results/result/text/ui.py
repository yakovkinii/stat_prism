from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

from core.mainwindow.layout import VerticalLayout
from core.mainwindow.results.preferred import createPreferredWidget
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

        self.layout = VerticalLayout(self.frame, padding_left=20, padding_right=20)

        self.title_widget = TitleWidget(self.frame, self.item.title)
        self.title_widget.setFixedWidth(999999)
        self.title_widget.adjustSize()

        self.layout.addWidget(self.title_widget)

        self.label = LabelClickable(self.frame)
        self.label.setWordWrap(True)
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.label.setAlignment(QtCore.Qt.AlignJustify)
        font = QtGui.QFont("Segoe UI")
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setText(item.text)
        #'Table (Study #0):' 107 21
        self.layout.addWidget(self.label)
'Summary (Study #0)'