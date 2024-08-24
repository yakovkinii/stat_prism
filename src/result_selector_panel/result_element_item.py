from typing import Callable

from PySide6 import QtWidgets
from PySide6.QtWidgets import QWidget

from src.common.result.registry import RESULTS
from src.common.unique_qss import set_stylesheet
from src.result_selector_panel.const import ClickAction


class ResultElementWidget(QWidget):
    def __init__(
        self,
        result_id: int,
        element_id: str,
        parent_widget,
        handler: Callable,
        selected_result: int,
        selected_element: str,
    ):
        super().__init__(parent_widget)

        self.result_id = result_id
        self.element_id = element_id
        self.handler = handler

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        result = RESULTS[result_id]
        element = result.result_elements[element_id]

        # Title
        self.widget = QtWidgets.QLabel(element.title)
        self.layout.addWidget(self.widget)

    def mousePressEvent(self, event):
        self.handler(action=ClickAction.ACTIVATE, result_id=self.result_id, element_id=self.element_id)
        event.accept()

    def refresh(self, selected_result: int, selected_element: str):
        if (self.element_id == selected_element) and (self.result_id == selected_result):
            set_stylesheet(
                self.widget,
                "#id{"
                "margin-top: 2px;"
                "font-family: Segoe UI;"
                "background-color: #f2f2f2;"
                "border: 1px solid #eee;"
                "border-left: 4px solid #7af;"
                "}",
            )
        else:
            set_stylesheet(
                self.widget,
                "#id{"
                "margin-top: 2px;"
                "font-family: Segoe UI;"
                "background-color: #f2f2f2;"
                "border: 1px solid #eee;"
                "border-left: 4px solid #ddd;"
                "}",
            )
