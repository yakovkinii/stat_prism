#  Copyright (c) 2023 StatPrism Team. All rights reserved.



import logging
from typing import TYPE_CHECKING

import pandas as pd
from PySide6 import QtWidgets
from PySide6.QtWidgets import QVBoxLayout

from src.common.elements.utility.layout_helpers import empty_widget
from src.common.result.registry import RESULTS
from src.main_area_panel.basic_main_area_panels.data_processing_panel import DataProcessing, DataProcessingConfig
from src.main_area_panel.panels.base import MainAreaItem
from src.main_area_panel.panels.data import DataItem
from src.pyside_ext.layout import VBoxLayout, HBoxLayout
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.result_display_panel.result_widget_containers.combined_result_widget_container import (
    CombinedResultElementWidgetContainer,
)
from src.result_display_panel.result_widget_containers.registry import result_widget_container_registry

if TYPE_CHECKING:
    from src.ui_main import MainWindowClass


class MainAreaClass:
    def __init__(self, parent_widget, parent_class, root_class):
        # Setup
        self.root_class: MainWindowClass = root_class
        self.parent_class: MainWindowClass = parent_class
        self.parent_widget = parent_widget

        self.widget, self.layout = empty_widget(
            parent=self.parent_widget,
            inner_layout_class=QVBoxLayout,
        )
        set_stylesheet(self.widget, css(background_color=Style.Color.Background))

        self.elements = []

        self.layout.addStretch()
        self.element_widget_container = None
        self.element_id = None
        self.result_id = None

        # ====
        self._keep_from_gc = None

    def add_data_processing(self, config: DataProcessingConfig):
        input_element = DataProcessing(
            config=config,
            parent_widget=self.widget,
            parent_class=self,
            root_class=self.root_class,
        )
        self.elements.append(input_element)
        self.layout.insertWidget(
            self.layout.count()-1, # Insert before the stretch
            input_element.widget,
        )

    # def cleanup(self):
    #     # Remove and delete the element widget container and its widget
    #     if self.element_widget_container is not None:
    #         try:
    #             # Remove from layout
    #             self.layout.removeWidget(self.element_widget_container.widget)
    #         except Exception:
    #             logging.error("Failed to remove widget from layout", exc_info=True)
    #         try:
    #             # Explicitly close the widget if it has a close method
    #             if hasattr(self.element_widget_container.widget, "close"):
    #                 self.element_widget_container.widget.close()
    #         except Exception:
    #             logging.error("Failed to close widget", exc_info=True)
    #         try:
    #             # Delete the widget later (Qt safe)
    #             self.element_widget_container.widget.deleteLater()
    #         except Exception:
    #             logging.error("Failed to delete widget", exc_info=True)
    #         # Remove strong references
    #         self._keep_from_gc = None
    #         self.element_widget_container = None
    #     self.result_id = None
    #     self.element_id = None



logging.debug("result display loaded")
