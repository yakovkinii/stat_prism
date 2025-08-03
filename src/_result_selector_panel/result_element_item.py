#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from typing import Callable

from PySide6 import QtWidgets
from PySide6.QtWidgets import QWidget

from src._result_selector_panel.const import ClickAction
from src.common.result.registry import RESULTS
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet


class ResultElementWidget(QWidget):
    def __init__(
        self,
        result_id: int,
        element_id: int,
        parent_widget,
        handler: Callable,
        selected_result: int,
        selected_element: int,
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
                css(
                    margin_top="2px",
                    font_family=Style.FontFamily.SegoeUI,
                    background_color=Style.Color.Background,
                    border=Style.General.border,
                    border_color=Style.Color.Highlight,
                    border_left="4px solid",
                    border_left_color=Style.Color.Highlight,
                ),
            )
        else:
            set_stylesheet(
                self.widget,
                css(
                    margin_top="2px",
                    font_family=Style.FontFamily.SegoeUI,
                    background_color=Style.Color.Background,
                    border=Style.General.border,
                    border_color=Style.Color.Border,
                    border_left="4px solid",
                    border_left_color=Style.Color.Border,
                ),
            )
