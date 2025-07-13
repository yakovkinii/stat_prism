#
#  Copyright (c) 2023 -- 2025 StatPrism Team. All rights reserved.
#

from typing import TYPE_CHECKING, Callable

from PySide6 import QtWidgets
from PySide6.QtWidgets import QFrame

from src.common.result.registry import RESULTS
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.result_selector_panel.const import ClickAction
from src.result_selector_panel.result_element_item import ResultElementWidget

if TYPE_CHECKING:
    pass


class ResultItemWidget(QFrame):
    def __init__(self, result_id: int, parent_widget, handler: Callable, selected_result: int, selected_element: str):
        super().__init__(parent_widget)

        self.result_id = result_id
        self.handler = handler

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)

        result = RESULTS[result_id]

        self.title_widget = QtWidgets.QLabel(result.title)

        self.context_widget = QtWidgets.QLabel(result.title_context)
        self.layout.addWidget(self.title_widget)
        self.layout.addWidget(self.context_widget)

        self.element_widgets = []
        for element_id, element in enumerate(result.result_elements):
            element_widget = ResultElementWidget(
                result_id=result_id,
                element_id=element_id,
                parent_widget=self,
                handler=handler,
                selected_result=selected_result,
                selected_element=selected_element,
            )
            self.element_widgets.append(element_widget)
            self.layout.addWidget(element_widget)

        self.refresh(selected_result, selected_element)

    def mousePressEvent(self, event):
        self.handler(action=ClickAction.ACTIVATE, result_id=self.result_id, element_id=None)
        super().mousePressEvent(event)

    def refresh(self, selected_result: int, selected_element: str):
        for widget in self.element_widgets:
            widget.refresh(selected_result, selected_element)

        if RESULTS[self.result_id].needs_update:
            set_stylesheet(
                self.title_widget,
                css(
                    font_weight="bold",
                    color=Style.Color.Danger,
                ),
            )
        else:
            set_stylesheet(
                self.title_widget,
                css(
                    font_weight="normal",
                    color=Style.Color.Text,
                ),
            )

        if self.result_id == selected_result:
            if selected_element is None:
                set_stylesheet(
                    self,
                    css(
                        margin_top="2px",
                        background_color=Style.Color.Background,
                        font_family=Style.FontFamily.SegoeUI,
                        border=Style.General.border,
                        border_color=Style.Color.Highlight,
                        border_left="4px solid",
                        border_left_color=Style.Color.Highlight,
                    ),
                )
            else:
                set_stylesheet(
                    self,
                    css(
                        margin_top="2px",
                        background_color=Style.Color.Background,
                        font_family=Style.FontFamily.SegoeUI,
                        border=Style.General.border,
                        border_color=Style.Color.Border,
                        border_left="4px solid",
                        border_left_color=Style.Color.Highlight,
                    ),
                )
        else:
            set_stylesheet(
                self,
                css(
                    margin_top="2px",
                    background_color=Style.Color.Background,
                    font_family=Style.FontFamily.SegoeUI,
                    border=Style.General.border,
                    border_color=Style.Color.Border,
                    border_left="4px solid",
                    border_left_color=Style.Color.Border,
                ),
            )
