from typing import TYPE_CHECKING

from PyQt5 import QtWidgets

from src.common.constant import DEBUG_LAYOUT
from src.common.unique_qss import set_stylesheet

if TYPE_CHECKING:
    from src.ui_main import MainWindowClass


class ResultSelectorClass:
    def __init__(self, parent_widget, parent_class, root_class):
        # Setup
        self.root_class: MainWindowClass = root_class
        self.parent_class: MainWindowClass = parent_class
        # tab widget
        self.widget = QtWidgets.QListWidget(parent_widget)
        # self.widget.setContentsMargins(0, 0, 0, 0)
        set_stylesheet(self.widget, "#id{background-color: #eef;}")
        self.widget.setFixedWidth(300)

        if DEBUG_LAYOUT:
            set_stylesheet(self.widget, "#id{border: 1px solid blue; background-color: #eef;}")

        self.widget.addItem("Result1")
        self.widget.addItem("Result2")