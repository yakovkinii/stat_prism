#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import logging

import qtawesome as qta
from PySide6.QtCore import QMimeData, QSize, Qt, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout

from src.common.decorators import log_method
from src.common.progress import with_progress
from src.common.ui_constructor import create_simple_tool_button_qta
from src.main_area_panel.result_display.base import BaseResultDisplay
from src.main_area_panel.result_display.elements.result_label import ResultLabel
from src.main_area_panel.result_display.plot_result_element import (
    PlotResultElementDisplay,
)
from src.main_area_panel.result_display.table_result_element import (
    TableResultElementDisplay,
)
from src.pyside_ext.elements.utility.layout_helpers import (
    empty_widget,
    widget_in_layout,
)
from src.pyside_ext.elements.utility.primitive_elements import QWidgetClickable
from src.pyside_ext.flow_layout import FlowLayout
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.modules.common.result.html_result import HTMLTableV2
from src.side_area_panel.modules.common.result.plot_result import PlotV2
from src.side_area_panel.modules.common.result.registry import RESULTS


class DataAnalysisResultDisplay(BaseResultDisplay):
    def __init__(self, parent_widget, parent_class, root_class, label_text: str, result_id):
        super().__init__(parent_widget, parent_class, root_class)
        self.result_id = result_id

        self.widget, self.layout = empty_widget(
            widget_class=QWidgetClickable,
            parent=self.parent_widget,
            inner_layout_class=QVBoxLayout,
            setup=lambda w, l: [
                l.setContentsMargins(10, 10, 5, 5),
                l.setSpacing(10),
                w.clicked.connect(lambda: self.activate_result(self.result_id, None)),
            ],
        )

        self.header_widget, self.header_layout = empty_widget(
            widget_class=QWidgetClickable,
            parent=self.widget,
            outer_layout=self.layout,
            inner_layout_class=QHBoxLayout,
            setup=lambda w, l: [w.clicked.connect(lambda: self.activate_result(self.result_id, None))],
        )

        self.label = widget_in_layout(
            widget=ResultLabel(parent=self.header_widget, label_text=label_text),
            layout=self.header_layout,
            setup=lambda w, l: [w.clicked.connect(lambda: self.activate_result(self.result_id, None))],
        )

        self.header_layout.addStretch()

        self.recalculate_button = widget_in_layout(
            widget=create_simple_tool_button_qta(
                parent=self.header_widget,
                icon_path="ph.arrows-clockwise-bold",
                icon_size=QSize(20, 20),
            ),
            layout=self.header_layout,
            alignment=Qt.AlignmentFlag.AlignTop,
            setup=lambda w, l: [
                w.setToolTip("Recalculate"),
                w.clicked.connect(self.recalculate),
            ],
        )

        self.delete_button = widget_in_layout(
            widget=create_simple_tool_button_qta(
                parent=self.header_widget,
                icon_path="mdi6.delete",
                icon_size=QSize(20, 20),
            ),
            layout=self.header_layout,
            alignment=Qt.AlignmentFlag.AlignTop,
            setup=lambda w, l: [
                w.setToolTip("Recalculate"),
                w.clicked.connect(self.delete),
            ],
        )
        self.deleting = False
        self.deleted = False

        self.copy_button = widget_in_layout(
            widget=create_simple_tool_button_qta(
                parent=self.header_widget,
                icon_path="fa.copy",
                icon_size=QSize(20, 20),
            ),
            layout=self.header_layout,
            alignment=Qt.AlignmentFlag.AlignTop,
            setup=lambda w, l: [
                w.setToolTip("Copy all result elements to clipboard"),
                w.clicked.connect(self.copy_all_elements),
            ],
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
            setup=lambda w, l: [
                l.setSpacing(5),
                w.clicked.connect(lambda: self.activate_result(self.result_id, None)),
            ],
        )

        self.display_element_id = None
        self.display_object = None
        self.element_display_objects = {}
        self.refresh()
        self.remove_focus(None)


    def copy_all_elements(self):
        self.copy_button.setIcon(qta.icon("fa.check", color="#4CAF50"))

        result = RESULTS[self.result_id]
        full_html = "<html><body>"

        for element in result.result_elements:
            if isinstance(element, HTMLTableV2):
                full_html += element.get_html()
            elif isinstance(element, PlotV2):
                full_html += element.get_html()
            full_html += "<br><br>"

        full_html += "</body></html>"

        mime_data = QMimeData()
        mime_data.setHtml(full_html)
        QGuiApplication.clipboard().setMimeData(mime_data)

        QTimer.singleShot(500, lambda: self.copy_button.setIcon(qta.icon("fa.copy", color="#888")))

    def recalculate(self):
        panel = self.root_class.settings_panel.panels[RESULTS[self.result_id].settings_panel_index]
        panel.configure(self.result_id)
        panel.recalculate()

    def delete(self):
        if not self.deleting:
            self.delete_button.setIcon(qta.icon("mdi6.delete-alert", color="#AF4C50"))
            self.deleting = True
            QTimer.singleShot(1500, lambda: self.set_not_deleting())
        else:
            self.deleted = True
            self.parent_class.delete_result(self.result_id)

    def set_not_deleting(self):
        if self.deleted:
            return
        self.delete_button.setIcon(qta.icon("mdi6.delete", color="#888"))
        self.deleting = False

    @log_method
    def set_display_element(self, result_element_id):
        self.display_element_id = result_element_id
        self.refresh_element(result_element_id)

    @log_method
    def unset_display_element(self, result_element_id):
        self.display_element_id = None
        self.refresh_element(result_element_id)

    def refresh_element(self, result_element_id):
        if result_element_id != self.display_element_id and self.display_object is not None:
            self.root_class.clean_up_main_area_display()
            logging.warning('Setting display_element_id = None')
            self.display_object = None
            self.display_element_id = None

        if result_element_id in self.element_display_objects:
            self.element_display_objects[result_element_id].refresh()
            if result_element_id==self.display_element_id:
                if self.display_object is None:
                    result_element = RESULTS[self.result_id].result_elements[result_element_id]
                    self.display_object = PlotResultElementDisplay(
                        parent_widget=self.plot_result_elements_container,
                        parent_class=self,
                        root_class=self.root_class,
                        label_text=result_element.title,
                        result_id=self.result_id,
                        result_element_id=result_element_id,
                    )
                    self.display_object.set_zoomed()
                    self.root_class.set_widget_in_main_area_display(self.display_object.widget)
                self.display_object.refresh()
                self.root_class.activate_main_area_display()
            else:
                self.root_class.activate_main_area_panel()
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
        for result_element_id, _ in enumerate(
            with_progress(
                RESULTS[self.result_id].result_elements,
                progress_bar=self.root_class.settings_panel.progress_bar,
            )
        ):
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
                    border_radius=Style.General.border_radius_medium,
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
                    border_radius=Style.General.border_radius_medium,
                ),
            )

        else:
            self.element_display_objects[focused_result_element_id].remove_focus(focused_result_element_id)
