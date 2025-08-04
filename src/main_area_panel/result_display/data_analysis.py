#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from PySide6.QtWidgets import QVBoxLayout

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
        )
        set_stylesheet(self.widget, css(background_color=Style.Color.Background))

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
            setup=lambda w, l: [
                w.clicked.connect(
                    lambda: self.activate_result(self.result_id, None)
                )
            ],
        )

        self.result_elements_container, self.result_elements_container_layout = empty_widget(
            parent=self.widget,
            outer_layout=self.layout,
            inner_layout_class=QVBoxLayout,
        )
        self.element_display_objects = {}

    def refresh_element(self, result_element_id):
        if result_element_id in self.element_display_objects:
            self.element_display_objects[result_element_id].refresh()
        else:
            result_element = RESULTS[self.result_id].result_elements[result_element_id]
            if isinstance(result_element, HTMLTableV2):
                self.element_display_objects[result_element_id] = TableResultElementDisplay(
                    parent_widget=self.widget,
                    parent_class=self,
                    root_class=self.root_class,
                    label_text=result_element.title,
                    result_id=self.result_id,
                    result_element_id=result_element_id,
                )
                self.result_elements_container_layout.addWidget(self.element_display_objects[result_element_id].widget)
            elif isinstance(result_element, PlotV2):
                self.element_display_objects[result_element_id] = PlotResultElementDisplay(
                    parent_widget=self.widget,
                    parent_class=self,
                    root_class=self.root_class,
                    label_text=result_element.title,
                    result_id=self.result_id,
                    result_element_id=result_element_id,
                )
                self.result_elements_container_layout.addWidget(self.element_display_objects[result_element_id].widget)

    def refresh(self):
        while self.result_elements_container_layout.count():
            item = self.result_elements_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.element_display_objects = {}
        for result_element_id, _ in enumerate(RESULTS[self.result_id].result_elements):
            self.refresh_element(result_element_id)
    @log_method

    def activate_result(self, result_id, result_element_id):
        self.parent_class.activate_result(result_id, result_element_id)
