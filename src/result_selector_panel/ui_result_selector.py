import logging
from typing import TYPE_CHECKING, Dict, Union

import qtawesome as qta
from PySide6 import QtWidgets
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QVBoxLayout

from src.common.decorators import log_method, log_method_noarg
from src.common.result.registry import RESULTS
from src.common.size import Font, SettingsPanelSize
from src.common.unique_qss import set_stylesheet
from src.result_selector_panel.const import ClickAction
from src.result_selector_panel.result_item import ResultItemWidget

if TYPE_CHECKING:
    from src.ui_main import MainWindowClass


class ResultSelectorPanelClass:
    def __init__(self, parent_widget, parent_class, root_class):
        # Setup
        self.root_class: MainWindowClass = root_class
        self.parent_class: MainWindowClass = parent_class

        self.widget = QtWidgets.QWidget(parent_widget)
        self.widget.setFixedWidth(SettingsPanelSize.width)
        self.widget.setContentsMargins(2, 0, 2, 0)
        set_stylesheet(self.widget, "#id{background-color: #fff;}")

        self.widget_layout = QVBoxLayout(self.widget)
        self.widget_layout.setContentsMargins(0, 0, 0, 0)
        self.widget_layout.setSpacing(0)
        self.widget.setLayout(self.widget_layout)

        self.scroll_area = QtWidgets.QScrollArea(self.widget)
        self.scroll_area.setWidgetResizable(True)
        set_stylesheet(self.scroll_area, "#id{border: none; background-color: #fff;}")

        self.scroll_area_widget = QtWidgets.QWidget(self.scroll_area)
        set_stylesheet(self.scroll_area_widget, "#id{background-color: #fff;}")
        self.scroll_area.setWidget(self.scroll_area_widget)
        self.scroll_area_layout = QVBoxLayout(self.scroll_area_widget)
        self.scroll_area_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area_layout.setSpacing(0)
        self.scroll_area_widget.setLayout(self.scroll_area_layout)

        self.results_list_widget = QtWidgets.QWidget(self.widget)

        self.scroll_area_layout.addWidget(self.results_list_widget)
        self.scroll_area_layout.addStretch()

        self.results_list_layout = QVBoxLayout(self.results_list_widget)
        self.results_list_layout.setContentsMargins(0, 0, 0, 0)
        self.results_list_layout.setSpacing(2)
        self.results_list_widget.setLayout(self.results_list_layout)

        self.add_result_button = QtWidgets.QPushButton("Add Result")
        set_stylesheet(
            self.add_result_button,
            "#id{"
            "margin-top: 2px;"
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
        self.add_result_button.setIcon(icon)
        self.add_result_button.setIconSize(QSize(32, 32))
        self.add_result_button.setFixedHeight(60)
        self.add_result_button.clicked.connect(
            lambda: self.parent_class.action_activate_panel_by_index(
                self.parent_class.settings_panel.select_study_panel_index
            )
        )

        self.widget_layout.addWidget(self.add_result_button)
        self.widget_layout.addWidget(self.scroll_area)

        self.result_widgets: Dict[int, ResultItemWidget] = {}
        self.selected_result: Union[int, None] = None
        self.selected_element: Union[str, None] = None

    @log_method
    def add_result(self, result_id: int):
        self.selected_result = result_id
        self.selected_element = None
        self.refresh_result(result_id)

    @log_method
    def refresh_result(self, result_id: int):
        if result_id in self.result_widgets:
            old_widget = self.result_widgets[result_id]
            position = self.results_list_layout.indexOf(old_widget)
            self.results_list_layout.removeWidget(old_widget)
            old_widget.deleteLater()
        else:
            position = self.results_list_layout.count()

        result_item_widget = ResultItemWidget(
            result_id=result_id,
            parent_widget=self.results_list_widget,
            handler=self.item_handler,
            selected_result=self.selected_result,
            selected_element=self.selected_element,
        )
        self.results_list_layout.insertWidget(position, result_item_widget)
        self.result_widgets[result_id] = result_item_widget
        self.refresh()

    def refresh(self):
        for widget in self.result_widgets.values():
            widget.refresh(self.selected_result, self.selected_element)

    @log_method
    def item_handler(self, action: ClickAction, result_id: int, element_id: str):
        logging.info(f"Item handler: {action} {result_id} {element_id}")
        if action == ClickAction.ACTIVATE:
            self.parent_class.settings_panel.panels[RESULTS[result_id].settings_panel_index].configure(result_id)
            self.parent_class.action_activate_panel_by_index(RESULTS[result_id].settings_panel_index)
            self.parent_class.results_panel.display(result_id=result_id, element_id=element_id)
            self.selected_result = result_id
            self.selected_element = element_id
            self.refresh()
            self.root_class.tab_widget.setCurrentIndex(1)
        elif action == ClickAction.DELETE:
            if element_id is None:
                raise NotImplementedError()
            else:
                raise NotImplementedError()

    @log_method_noarg
    def delete_all_results(self):
        raise NotImplementedError()


logging.debug("results loaded")
