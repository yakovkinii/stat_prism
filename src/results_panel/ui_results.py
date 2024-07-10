from typing import TYPE_CHECKING, Dict

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QHBoxLayout

from src.common.constant import DEBUG_LAYOUT
from src.common.unique_qss import set_stylesheet
from src.results_panel.result_display import ResultDisplayClass
from src.results_panel.result_selector import ResultSelectorClass
from src.results_panel.results.common.base import BaseResult

if TYPE_CHECKING:
    from src.ui_main import MainWindowClass


class ResultsPanelClass:
    def __init__(self, parent_widget, parent_class, root_class):
        # Setup
        self.root_class: MainWindowClass = root_class
        self.parent_class: MainWindowClass = parent_class
        self.widget = QtWidgets.QWidget(parent_widget)
        self.widget.setContentsMargins(10, 0, 0, 0)
        set_stylesheet(self.widget, "#id{background-color: #fff;}")

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

        self.results: Dict[int, BaseResult] = {}

    def add_result(self, result: BaseResult):
        self.results[result.unique_id] = result
        self.result_selector.add_result(self.results[result.unique_id])
        self.result_display.configure(self.results[result.unique_id])

    def update_result(self, result: BaseResult):
        self.results[result.unique_id] = result
        # self.result_selector.update_result(result)
        self.result_display.configure(result)

    def get_unique_id(self):
        return max(self.results.keys()) + 1 if len(self.results) > 0 else 1