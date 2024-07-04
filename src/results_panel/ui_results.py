import logging
from typing import TYPE_CHECKING

from PyQt5 import  QtWidgets
from PyQt5.QtWidgets import QHBoxLayout

from src.common.constant import DEBUG_LAYOUT
from src.common.unique_qss import set_stylesheet
from src.results_panel.result_display import ResultDisplayClass
from src.results_panel.result_selector import ResultSelectorClass

if TYPE_CHECKING:
    from src.ui_main import MainWindowClass


class ResultsPanelClass:
    def __init__(self, parent_widget, parent_class, root_class):
        # Setup
        self.root_class: MainWindowClass = root_class
        self.parent_class: MainWindowClass = parent_class
        self.widget = QtWidgets.QWidget(parent_widget)
        self.widget.setContentsMargins(10, 0, 0, 0)

        if DEBUG_LAYOUT:
            set_stylesheet(self.widget, "#id{border: 1px solid blue; background-color: #eef;}")
        self.widget_layout = QHBoxLayout(self.widget)
        self.widget_layout.setContentsMargins(0, 0, 0, 0)
        self.widget.setLayout(self.widget_layout)

        # Definition
        self.result_selector = ResultSelectorClass(
            parent_widget=self.widget,
            parent_class=self,
            root_class=root_class,
        )
        self.result_display = ResultDisplayClass(
            parent_widget=self.widget,
            parent_class=self,
            root_class=root_class,
        )

        self.widget_layout.addWidget(self.result_display.widget)
        self.widget_layout.addWidget(self.result_selector.widget)
