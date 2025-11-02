#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import logging
from typing import TYPE_CHECKING

from PySide6 import QtWidgets
from PySide6.QtWidgets import QVBoxLayout

from src.common.decorators import log_method
from src.main_area_panel.result_display.data_analysis import DataAnalysisResultDisplay
from src.main_area_panel.result_display.data_processing import (
    DataProcessingResultDisplay,
)
from src.main_area_panel.result_display.raw_data import RawDataResultDisplay
from src.pyside_ext.elements.utility.layout_helpers import empty_widget
from src.pyside_ext.elements.utility.primitive_elements import QWidgetClickable
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.modules.common.result.registry import RESULTS
from src.side_area_panel.registry import PanelRegistry

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
            widget_class=QWidgetClickable,
            parent=self.parent_widget,
            inner_layout_class=QVBoxLayout,
            setup=lambda w, l: [
                l.setSpacing(10),
                w.clicked.connect(lambda: self.activate_result(None, None)),
            ],
        )
        self.widget.setWidget(self.widget_in_scroll_area)

        set_stylesheet(self.widget_in_scroll_area, css(background_color=Style.Color.Background))

        # Raw Data
        self.raw_data_widget_container, self.raw_data_container_layout = empty_widget(
            widget_class=QWidgetClickable,
            parent=self.widget_in_scroll_area,
            outer_layout=self.layout,
            inner_layout_class=QVBoxLayout,
            setup=lambda w, l: [
                l.setContentsMargins(10, 10, 5, 5),
                l.setSpacing(10),
                w.clicked.connect(lambda: self.activate_result(None, None)),
            ],
        )

        # Data Processing
        self.data_processing_widget_container, self.data_processing_container_layout = empty_widget(
            widget_class=QWidgetClickable,
            parent=self.widget_in_scroll_area,
            outer_layout=self.layout,
            inner_layout_class=QVBoxLayout,
            setup=lambda w, l: [
                l.setContentsMargins(10, 10, 5, 5),
                l.setSpacing(10),
                w.clicked.connect(lambda: self.activate_result(None, None)),
            ],
        )

        # Data Analysis
        self.data_analysis_widget_container, self.data_analysis_container_layout = empty_widget(
            widget_class=QWidgetClickable,
            parent=self.widget_in_scroll_area,
            outer_layout=self.layout,
            inner_layout_class=QVBoxLayout,
            setup=lambda w, l: [
                l.setContentsMargins(10, 10, 5, 5),
                l.setSpacing(10),
                w.clicked.connect(lambda: self.activate_result(None, None)),
            ],
        )

        self.layout.addStretch()

        self.focused_result_id = None
        self.focused_result_element_id = None

        self.raw_data_objects = {}
        self.data_processing_objects = {}
        self.data_analysis_objects = {}

    def add_raw_data(self, result_id):
        raw_data_object = RawDataResultDisplay(
            parent_widget=self.raw_data_widget_container,
            parent_class=self,
            root_class=self.root_class,
            label_text=RESULTS[result_id].title,
            result_id=result_id,
        )
        self.raw_data_objects[result_id] = raw_data_object
        self.raw_data_container_layout.addWidget(raw_data_object.widget)

    def add_data_processing(self, result_id):
        data_processing_object = DataProcessingResultDisplay(
            parent_widget=self.data_processing_widget_container,
            parent_class=self,
            root_class=self.root_class,
            label_text=RESULTS[result_id].title,
            result_id=result_id,
        )
        self.data_processing_objects[result_id] = data_processing_object
        self.data_processing_container_layout.addWidget(data_processing_object.widget)

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

    def get_result_object(self, result_id):
        return (
            self.data_analysis_objects.get(result_id)
            or self.data_processing_objects.get(result_id)
            or self.raw_data_objects.get(result_id)
        )

    def refresh_result(self, result_id, result_element_id=None):
        result_object = self.get_result_object(result_id)
        if result_element_id is None:
            result_object.refresh()
        else:
            result_object.refresh_element(result_element_id)

    def update_focus(self, result_id, result_element_id=None):
        if self.focused_result_id is not None:
            self.get_result_object(self.focused_result_id).remove_focus(self.focused_result_element_id)

        self.focused_result_id = result_id
        self.focused_result_element_id = result_element_id
        if result_id is not None:
            self.get_result_object(result_id).set_focus(result_element_id)

    @log_method
    def activate_result(self, result_id, result_element_id):
        logging.warning(f"Activating result {result_id} with element {result_element_id}")
        if result_element_id is None:
            if result_id is None:
                if len(RESULTS) == 0:
                    self.parent_class.action_activate_panel_by_index(
                        PanelRegistry.HOME_INITIAL.settings_stacked_widget_index
                    )
                else:
                    self.parent_class.action_activate_panel_by_index(PanelRegistry.HOME.settings_stacked_widget_index)
            else:
                self.parent_class.settings_panel.panels[RESULTS[result_id].settings_panel_index].configure(result_id)
                self.parent_class.action_activate_panel_by_index(RESULTS[result_id].settings_panel_index)
        else:
            self.parent_class.action_activate_panel_by_index(
                RESULTS[result_id].result_elements[result_element_id].settings_panel_index
            )
            self.parent_class.settings_panel.panels[
                RESULTS[result_id].result_elements[result_element_id].settings_panel_index
            ].configure(result_id, result_element_id)
        self.update_focus(result_id, result_element_id)

    def remove_result(self, result_id):
        # Remove from UI and object dicts
        obj = self.get_result_object(result_id)

        # Remove widget from layout
        if result_id in self.data_analysis_objects:
            layout = self.data_analysis_container_layout
            del self.data_analysis_objects[result_id]
        elif result_id in self.data_processing_objects:
            layout = self.data_processing_container_layout
            del self.data_processing_objects[result_id]
        elif result_id in self.raw_data_objects:
            layout = self.raw_data_container_layout
            del self.raw_data_objects[result_id]
        else:
            return
        layout.removeWidget(obj.widget)
        obj.widget.setParent(None)
        obj.widget.deleteLater()

        # Update focus if needed
        if self.focused_result_id == result_id:
            self.focused_result_id = None
            self.focused_result_element_id = None
        self.activate_result(None, None)
