from typing import TYPE_CHECKING

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QProxyStyle, QTabWidget, QStyleFactory

from src.common.constant import DEBUG_LAYOUT
from src.common.unique_qss import set_stylesheet

if TYPE_CHECKING:
    from src.ui_main import MainWindowClass

class ResetStyle(QProxyStyle):
    def __init__(self, base_style=None):
        super().__init__(base_style)

    def drawPrimitive(self, element, option, painter, widget):
        super().drawPrimitive(element, option, painter, widget)

    def drawControl(self, element, option, painter, widget):
        super().drawControl(element, option, painter, widget)

    def drawComplexControl(self, element, option, painter, widget):
        super().drawComplexControl(element, option, painter, widget)


class ResultDisplayClass:
    def __init__(self, parent_widget, parent_class, root_class):
        # Setup
        self.root_class: MainWindowClass = root_class
        self.parent_class: MainWindowClass = parent_class
        # tab widget
        self.widget = QtWidgets.QTabWidget()
        self.widget.setStyle(ResetStyle(QStyleFactory.create("Fusion")))
        # self.widget.setContentsMargins(0, 0, 0, 0)
        self.widget.tabBar().setDocumentMode(True)
        self.widget.tabBar().setExpanding(True)

        if DEBUG_LAYOUT:
            set_stylesheet(self.widget, "#id{border: 1px solid blue; background-color: #eef;}")

        self.widget.addTab(QtWidgets.QLabel("Result1"), "Result1")
        self.widget.addTab(QtWidgets.QLabel("Result2"), "Result2")
        # Increase the minimum size for tabs to prevent cutting off

        # Adjust the style of the tabs for better appearance


