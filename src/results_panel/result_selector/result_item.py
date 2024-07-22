from typing import TYPE_CHECKING

from PySide6 import QtWidgets
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QWidget

from src.common.size import Font
from src.common.unique_qss import set_stylesheet
from src.results_panel.results.common.base import BaseResult

if TYPE_CHECKING:
    pass


class ResultListItem(QWidget):
    """
    The very item displayed
    """

    def __init__(self, result_id: int, result: BaseResult, parent_widget, click_handler, delete_handler):
        super().__init__(parent_widget)

        self.result_id: int = result_id
        self.result = result
        self.click_handler = click_handler
        self.delete_handler = delete_handler

        self.layout = QtWidgets.QVBoxLayout(self)
        self.title_widget = QtWidgets.QLabel(self.result.title)
        self.context_widget = QtWidgets.QLabel(self.result.title_context + str(self.result.config.filter_id))
        self.layout.addWidget(self.title_widget)
        self.layout.addWidget(self.context_widget)

        set_stylesheet(
            self.title_widget,
            (
                "#id{" + ("color: #700;" if result.needs_update else "color: #000") + "font-family: Segoe UI;"
                f"font-size: {Font.size}pt;"
                "}"
            ),
        )
        set_stylesheet(
            self.context_widget, "#id{" "color: #000;" "font-family: Segoe UI;" f"font-size: {Font.size_small}pt;" "}"
        )

    def mousePressEvent(self, event):
        if self.click_handler is not None:
            self.click_handler(self.result_id)
        super().mousePressEvent(event)

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        delete_action = QAction("Delete", self)
        context_menu.addAction(delete_action)

        # Connect the 'delete' action to the slot/function
        delete_action.triggered.connect(self.delete_handler)

        # Show the menu at the cursor's current position
        context_menu.exec_(event.globalPos())

    def refresh(self):
        set_stylesheet(
            self.title_widget,
            (
                "#id{" + ("color: #700;" if self.result.needs_update else "color: #000") + "font-family: Segoe UI;"
                f"font-size: {Font.size}pt;"
                "}"
            ),
        )
