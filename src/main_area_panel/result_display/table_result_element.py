#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import logging

import qtawesome as qta
from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout

from src.common.constant import BASE_STYLES
from src.common.decorators import log_method
from src.common.ui_constructor import create_simple_tool_button_qta
from src.main_area_panel.result_display.base import BaseResultDisplay
from src.main_area_panel.result_display.elements.text_browser import TextBrowser
from src.pyside_ext.elements.utility.layout_helpers import empty_widget
from src.pyside_ext.elements.utility.primitive_elements import QWidgetClickable
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.modules.common.result.html_result import HTMLTableV2
from src.side_area_panel.modules.common.result.registry import RESULTS


class TableResultElementDisplay(BaseResultDisplay):
    def __init__(self, parent_widget, parent_class, root_class, label_text: str, result_id, result_element_id):
        super().__init__(parent_widget, parent_class, root_class)
        self.result_id = result_id
        self.result_element_id = result_element_id

        self.widget, self.layout = empty_widget(
            widget_class=QWidgetClickable,
            parent=self.parent_widget,
            inner_layout_class=QGridLayout,
            setup=lambda w, l: [
                w.clicked.connect(lambda: self.activate_result(self.result_id, self.result_element_id)),
            ],
        )
        self.layout.setContentsMargins(5, 2, 5, 2)
        self.layout.setSpacing(0)

        self.text_browser = TextBrowser(self.widget)
        self.text_browser.clicked.connect(lambda: self.activate_result(self.result_id, self.result_element_id))
        self.text_browser.setMinimumWidth(500)
        set_stylesheet(self.text_browser, css(border="none"))
        self.layout.addWidget(self.text_browser, 0, 0)

        # The copy button overlays the table's top-right corner (same grid cell) instead of
        # sitting in a header row, so it adds no vertical gap above the caption (the title is
        # rendered inside the table HTML).
        self.copy_button = create_simple_tool_button_qta(
            parent=self.widget,
            icon_path="fa.copy",
            icon_size=QtCore.QSize(20, 20),
        )
        self.copy_button.setToolTip("Copy result element to clipboard")
        self.copy_button.clicked.connect(self.copy_table)
        self.layout.addWidget(
            self.copy_button, 0, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight
        )
        self.copy_button.raise_()

        self.refresh()
        self.remove_focus(self.result_element_id)

    def refresh(self):
        table: HTMLTableV2 = RESULTS[self.result_id].result_elements[self.result_element_id]
        self.text_browser.set_html(BASE_STYLES + table.get_html())
        # Title is rendered inside the table HTML now, so there is no separate header label.

    @log_method
    def activate_result(self, result_id, result_element_id):
        self.parent_class.activate_result(result_id, result_element_id)

    def set_focus(self, focused_result_element_id):
        logging.warning(f"Setting focus on {self.result_id} with element {focused_result_element_id}")
        assert focused_result_element_id is not None
        set_stylesheet(
            self.widget,
            css(
                border=Style.General.border_thin_selected_element,
                border_radius="5px",
            ),
        )

    @log_method
    def remove_focus(self, focused_result_element_id):
        logging.warning(f"Removing focus from {self.result_id} with element {focused_result_element_id}")
        assert focused_result_element_id is not None
        set_stylesheet(
            self.widget,
            css(
                border=Style.General.border_thin_unselected,
                border_radius="5px",
            ),
        )

    def copy_table(self):
        self.copy_button.setIcon(qta.icon("fa.check", color=Style.Color.SimpleToolButton.value))
        self.text_browser.copy_to_clipboard()
        QtCore.QTimer.singleShot(500, lambda: self.copy_button.setIcon(qta.icon("fa.copy", color="#888")))
