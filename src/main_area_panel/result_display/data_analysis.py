#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import logging

from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

from src.common.decorators import log_method
from src.common.elements.utility.layout_helpers import empty_widget, widget_in_layout
from src.common.elements.utility.primitive_elements import QWidgetClickable
from src.common.result.html_result import HTMLTableV2
from src.common.result.plot_result import PlotV2
from src.common.result.registry import RESULTS
from src.main_area_panel.result_display.base import BaseResultDisplay
from src.main_area_panel.result_display.elements.result_label import ResultLabel
from src.main_area_panel.result_display.plot_result_element import PlotResultElementDisplay
from src.main_area_panel.result_display.table_result_element import TableResultElementDisplay
from src.pyside_ext.flow_layout import FlowLayout
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet


class DataAnalysisResultDisplay(BaseResultDisplay):
    def __init__(self, parent_widget, parent_class, root_class, label_text: str, result_id):
        super().__init__(parent_widget, parent_class, root_class)
        self.result_id = result_id

        self.widget, self.layout = empty_widget(
            parent=self.parent_widget,
            inner_layout_class=QVBoxLayout,
            setup=lambda w, l: [
                l.setContentsMargins(10, 10, 5, 5),
                l.setSpacing(10),
            ],
        )


        self.header_widget, self.header_layout = empty_widget(
            widget_class=QWidgetClickable,
            parent=self.widget,
            outer_layout=self.layout,
            inner_layout_class=QVBoxLayout,
            setup=lambda w, l: [w.clicked.connect(lambda: self.activate_result(self.result_id, None))],
        )

        self.label = widget_in_layout(
            widget=ResultLabel(parent=self.header_widget, label_text=label_text),
            layout=self.header_layout,
            setup=lambda w, l: [w.clicked.connect(lambda: self.activate_result(self.result_id, None))],
        )

        self.html_result_elements_container, self.html_result_elements_container_layout = empty_widget(
            widget_class=QWidgetClickable,
            parent=self.widget,
            outer_layout=self.layout,
            inner_layout_class=QVBoxLayout,
            setup=lambda w, l: [
                l.setSpacing(5),
                w.clicked.connect(lambda: self.activate_result(self.result_id, None)),
            ],
        )

        self.plot_result_elements_container, self.plot_result_elements_container_layout = empty_widget(
            widget_class=QWidgetClickable,
            parent=self.widget,
            outer_layout=self.layout,
            inner_layout_class=FlowLayout,
            setup= lambda w, l: [
                l.setSpacing(5),
                w.clicked.connect(lambda: self.activate_result(self.result_id, None)),
            ]
        )


        self.element_display_objects = {}
        self.remove_focus(None)

    def refresh_element(self, result_element_id):
        if result_element_id in self.element_display_objects:
            self.element_display_objects[result_element_id].refresh()
        else:
            result_element = RESULTS[self.result_id].result_elements[result_element_id]
            if isinstance(result_element, HTMLTableV2):
                self.element_display_objects[result_element_id] = TableResultElementDisplay(
                    parent_widget=self.html_result_elements_container,
                    parent_class=self,
                    root_class=self.root_class,
                    label_text=result_element.title,
                    result_id=self.result_id,
                    result_element_id=result_element_id,
                )
                self.html_result_elements_container_layout.addWidget(
                    self.element_display_objects[result_element_id].widget
                )
            elif isinstance(result_element, PlotV2):
                self.element_display_objects[result_element_id] = PlotResultElementDisplay(
                    parent_widget=self.plot_result_elements_container,
                    parent_class=self,
                    root_class=self.root_class,
                    label_text=result_element.title,
                    result_id=self.result_id,
                    result_element_id=result_element_id,
                )
                self.plot_result_elements_container_layout.addWidget(
                    self.element_display_objects[result_element_id].widget
                )
        # self.adjust_scroll_height()

    def adjust_scroll_height(self):
        self.plot_result_elements_container.adjustSize()
        height = self.plot_result_elements_container.sizeHint().height()
        self.scroll_area.setFixedHeight(height + self.scroll_area.horizontalScrollBar().height())

    def refresh(self):
        while self.html_result_elements_container_layout.count():
            item = self.html_result_elements_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        while self.plot_result_elements_container_layout.count():
            item = self.plot_result_elements_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.element_display_objects = {}
        for result_element_id, _ in enumerate(RESULTS[self.result_id].result_elements):
            self.refresh_element(result_element_id)

    @log_method
    def activate_result(self, result_id, result_element_id):
        self.parent_class.activate_result(result_id, result_element_id)

    def set_focus(self, focused_result_element_id):
        logging.warning(f"Setting focus on {self.result_id} with element {focused_result_element_id}")
        if focused_result_element_id is None:
            set_stylesheet(
                self.widget,
                css(
                    background_color=Style.Color.Background,
                    border=Style.General.border_thin_selected,
                    border_left=Style.General.border_thick_selected,
                    border_radius="5px",
                ),
            )
        else:
            self.element_display_objects[focused_result_element_id].set_focus(focused_result_element_id)

    def remove_focus(self, focused_result_element_id):
        logging.warning(f"Removing focus from {self.result_id} with element {focused_result_element_id}")
        if focused_result_element_id is None:
            set_stylesheet(
                self.widget,
                css(
                    background_color=Style.Color.Background,
                    border=Style.General.border_thin_unselected,
                    border_left=Style.General.border_thick_unselected,
                    border_radius="5px",
                ),
            )

        else:
            self.element_display_objects[focused_result_element_id].remove_focus(focused_result_element_id)