import logging
from typing import TYPE_CHECKING
import qtawesome as qta

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QWidget, QListWidgetItem

from src.common.constant import DEBUG_LAYOUT
from src.common.decorators import log_method
from src.common.unique_qss import set_stylesheet
from src.results_panel.results.base_result import BaseResult

if TYPE_CHECKING:
    from src.ui_main import MainWindowClass


class ResultListItem(QWidget):
    def __init__(self, unique_id, parent_widget=None, title="", handler=None):
        super().__init__(parent_widget)

        self.unique_id = unique_id
        self.title = title
        self.handler = handler

        self.layout = QtWidgets.QHBoxLayout(self)
        title_widget = QtWidgets.QLabel(title)
        self.layout.addWidget(title_widget)

        set_stylesheet(title_widget, "#id{" "color: #000;" "font-family: Segoe UI;" "font-size: 18px;" "}")

    def mousePressEvent(self, event):
        if self.handler is not None:
            self.handler(self.unique_id)
        super().mousePressEvent(event)


class ResultSelectorClass:
    def __init__(self, parent_widget, parent_class, root_class):
        # Setup
        self._width = 255
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
            "font-size: 18px;"
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

        self.list_widget = QtWidgets.QListWidget(self.widget)

        set_stylesheet(
            self.list_widget,
            "#id{"
            "border: 1px solid #ddd;"
            "outline: 0;"
            "}"
            "#id::item:selected{"
            "background-color: rgb(229,241,251);"
            "border: 1px solid rgb(0,120,215)"
            "}",
        )

        # self.list_widget.setFixedWidth(self._width)
        self.widget_layout.addWidget(self.list_widget)
        if DEBUG_LAYOUT:
            set_stylesheet(self.widget, "#id{border: 1px solid blue; background-color: #eef;}")

        # self.widget.addItem("Result1")
        # self.widget.addItem("Result2")

    @log_method
    def add_result(self, result: BaseResult):
        # remove the last item in list

        item = QListWidgetItem()

        widget = ResultListItem(
            unique_id=result.unique_id,
            title=result.title,
            handler=self.activate_result_handler,
            parent_widget=self.list_widget,
        )
        widget.setFocusPolicy(QtCore.Qt.NoFocus)
        item.setSizeHint(widget.sizeHint())
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, widget)

        self.list_widget.setCurrentRow(self.list_widget.count() - 1)

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
