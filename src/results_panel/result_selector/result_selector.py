import logging
from typing import TYPE_CHECKING

import qtawesome as qta
from PySide6 import QtWidgets
from PySide6.QtCore import QSize

from src.common.constant import DEBUG_LAYOUT
from src.common.decorators import log_method, log_method_noarg
from src.common.size import Font
from src.common.unique_qss import set_stylesheet
from src.results_panel.result_selector.lists import DragDropListWidget
from src.results_panel.results.common.base import BaseResult

if TYPE_CHECKING:
    from src.ui_main import MainWindowClass


class ResultSelectorClass:
    def __init__(self, parent_widget, parent_class, root_class):
        """
        list of results is drawn here in order.
        The items are identified by result id.

        """
        # Setup
        self._width = 220
        self.root_class: MainWindowClass = root_class
        self.parent_class: MainWindowClass = parent_class
        self.widget = QtWidgets.QWidget(parent_widget)
        self.widget.setFixedWidth(self._width)

        self.widget_layout = QtWidgets.QVBoxLayout(self.widget)
        self.widget_layout.setContentsMargins(0, 0, 5, 0)

        button = QtWidgets.QPushButton("Add Study")
        button.clicked.connect(self.add_result_handler)
        # font size
        set_stylesheet(
            button,
            "#id{"
            "background-color: #fff;"
            "font-family: Segoe UI;"
            f"font-size: {Font.size}pt;"
            "border: 1px solid #ddd;"
            "}"
            "#id:hover{"
            "background-color: rgb(229,241,251);"
            "border: 1px solid rgb(0,120,215)"
            "}",
        )
        icon = qta.icon("fa5s.plus")
        button.setIcon(icon)
        button.setIconSize(QSize(32, 32))
        button.setFixedHeight(60)

        self.widget_layout.addWidget(button)

        self.list_widget = DragDropListWidget(
            self.widget, root_class, self.activate_result_handler, self.delete_result_handler
        )

        # self.list_widget.setFixedWidth(self._width)
        self.widget_layout.addWidget(self.list_widget)
        if DEBUG_LAYOUT:
            set_stylesheet(self.widget, "#id{border: 1px solid blue; background-color: #eef;}")

        # self.widget.addItem("Result1")
        # self.widget.addItem("Result2")

    @log_method_noarg
    def add_all_results(self):
        for result in self.root_class.results_panel.results.values():
            self.add_result(result)

    @log_method
    def add_result(self, result: BaseResult):
        self.list_widget.addItemWithCustomWidget(result.unique_id)

    @log_method
    def add_result_handler(self, *args, **kwargs):
        logging.info("Trying to add result")
        self.root_class.action_activate_panel_by_index(self.root_class.settings_panel.select_study_panel_index)

    @log_method
    def activate_result_handler(self, unique_id):
        logging.info(f"Trying to activate result with unique_id: {unique_id}")
        result = self.root_class.results_panel.results[unique_id]

        self.root_class.settings_panel.panels[result.settings_panel_index].configure(result=result)
        self.root_class.action_activate_panel_by_index(result.settings_panel_index)
        self.root_class.results_panel.result_display.configure(self.root_class.results_panel.results[unique_id])

    @log_method
    def delete_result_handler(self, unique_id):
        logging.info(f"Trying to delete result with unique_id: {unique_id}")
        result_index = self.list_widget.currentRow()
        self.list_widget.takeItem(result_index)
        self.root_class.results_panel.results.pop(unique_id)
        if self.root_class.results_panel.results:
            self.activate_result_handler(list(self.root_class.results_panel.results.keys())[0])
            self.list_widget.setCurrentRow(0)

    @log_method
    def update_all(self):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            widget = self.list_widget.itemWidget(item)
            widget.refresh()
