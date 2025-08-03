#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from typing import TYPE_CHECKING

from PySide6 import QtWidgets
from PySide6.QtWidgets import QVBoxLayout

from src.common.elements.utility.layout_helpers import empty_widget
from src.common.result.registry import RESULTS
from src.main_area_panel.result_display.data_analysis import DataAnalysisResultDisplay
from src.main_area_panel.result_display.data_processing import DataProcessingResultDisplay
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet

if TYPE_CHECKING:
    from src.ui_main import MainWindowClass


class MainAreaClass:
    def __init__(self, parent_widget, parent_class, root_class):
        # Setup
        self.root_class: MainWindowClass = root_class
        self.parent_class: MainWindowClass = parent_class
        self.parent_widget = parent_widget

        self.widget = QtWidgets.QScrollArea()
        set_stylesheet(self.widget, css(border="none", background_color=Style.Color.Background)),
        self.widget.setWidgetResizable(True),

        self.widget_in_scroll_area, self.layout = empty_widget(
            parent=self.parent_widget,
            inner_layout_class=QVBoxLayout,
        )
        self.widget.setWidget(self.widget_in_scroll_area)

        set_stylesheet(self.widget_in_scroll_area, css(background_color=Style.Color.Background))

        # Raw Data
        self.raw_data_widget_container, self.raw_data_container_layout = empty_widget(
            parent=self.widget_in_scroll_area,
            outer_layout=self.layout,
            inner_layout_class=QVBoxLayout,
        )

        # Data Processing
        # ...

        # Data Analysis
        self.data_analysis_widget_container, self.data_analysis_container_layout = empty_widget(
            parent=self.widget_in_scroll_area,
            outer_layout=self.layout,
            inner_layout_class=QVBoxLayout,
        )

        self.layout.addStretch()

        # For GC
        self.raw_data_object = None
        self.data_analysis_objects = {}

    def refresh_raw_data(self):
        self.raw_data_object = DataProcessingResultDisplay(
            parent_widget=self.raw_data_widget_container,
            parent_class=self,
            root_class=self.root_class,
            label_text="Raw Data",
            data_item_index=0,
        )

        # Clean up raw_data_container_layout
        while self.raw_data_container_layout.count():
            item = self.raw_data_container_layout.takeAt(0)
            if item.widget_in_scroll_area():
                item.widget_in_scroll_area().deleteLater()

        self.raw_data_container_layout.insertWidget(
            0,
            self.raw_data_object.widget,
        )

    def add_data_analysis(self, result_id):
        data_analysis_object = DataAnalysisResultDisplay(
            parent_widget=self.data_analysis_widget_container,
            parent_class=self,
            root_class=self.root_class,
            label_text=RESULTS[result_id].title,
            result_id=result_id,
        )

        self.data_analysis_objects[result_id] = data_analysis_object

        self.data_analysis_container_layout.addWidget(data_analysis_object.widget)

    def refresh_data_analysis(self, result_id):
        self.data_analysis_objects[result_id].refresh()
