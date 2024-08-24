from typing import TYPE_CHECKING, Callable

from PySide6 import QtWidgets
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QFrame, QMenu

from src.common.result.registry import RESULTS
from src.common.unique_qss import set_stylesheet
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
        # self.titles = []
        # self.class_ids = []
        # self.widgets = []
        for element_id, element in result.result_elements.items():
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

    # def contextMenuEvent(self, event):
    #     context_menu = QMenu(self)
    #     delete_action = QAction("Delete", self)
    #     context_menu.addAction(delete_action)
    #
    #     delete_action.triggered.connect(
    #         lambda: self.handler(action=ClickAction.DELETE, result_id=self.result_id, element_id=None)
    #     )
    #     context_menu.exec_(event.globalPos())

    def refresh(self, selected_result: int, selected_element: str):
        for widget in self.element_widgets:
            widget.refresh(selected_result, selected_element)

        if self.result_id == selected_result:
            set_stylesheet(
                self,
                "#id{"
                "margin-top: 2px;"
                "background-color: #fff;"
                "font-family: Segoe UI;"
                "border: 2px solid #eee;"
                "border-left: 4px solid #7af;"
                "}",
            )
        else:
            set_stylesheet(
                self,
                "#id{"
                "margin-top: 2px;"
                "background-color: #fff;"
                "font-family: Segoe UI;"
                "border: 2px solid #eee;"
                "border-left: 4px solid #ddd;"
                "}",
            )
