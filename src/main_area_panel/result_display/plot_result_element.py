#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import logging

import qtawesome as qta
from PySide6 import QtCore
from PySide6.QtCore import QMimeData, QSize, Qt
from PySide6.QtGui import QGuiApplication, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from src.common.decorators import log_method
from src.common.ui_constructor import create_simple_tool_button_qta
from src.main_area_panel.result_display.base import BaseResultDisplay
from src.main_area_panel.result_display.elements.result_element_label import (
    ResultElementLabel,
)
from src.pyside_ext.elements.utility.layout_helpers import (
    empty_widget,
    widget_in_layout,
)
from src.pyside_ext.elements.utility.primitive_elements import (
    QLabelClickable,
    QWidgetClickable,
)
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.modules.common.result.registry import RESULTS


class PlotResultElementDisplay(BaseResultDisplay):
    def __init__(self, parent_widget, parent_class, root_class, label_text: str, result_id, result_element_id):
        super().__init__(parent_widget, parent_class, root_class)
        self.result_id = result_id
        self.result_element_id = result_element_id

        self.widget, self.layout = empty_widget(
            widget_class=QWidgetClickable,
            parent=self.parent_widget,
            inner_layout_class=QVBoxLayout,
            setup=lambda w, l: [
                w.clicked.connect(lambda: self.activate_result(self.result_id, self.result_element_id)),
            ],
        )
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        self.header_widget, self.header_layout = empty_widget(
            widget_class=QWidgetClickable,
            parent=self.widget,
            outer_layout=self.layout,
            inner_layout_class=QHBoxLayout,
            setup=lambda w, l: [
                w.clicked.connect(lambda: self.activate_result(self.result_id, self.result_element_id)),
                l.setSpacing(5),
            ],
        )

        self.label = widget_in_layout(
            widget=ResultElementLabel(parent=self.header_widget, label_text=""),
            layout=self.header_layout,
            setup=lambda w, l: [
                w.clicked.connect(lambda: self.activate_result(self.result_id, self.result_element_id))
            ],
        )

        self.copy_button = widget_in_layout(
            widget=create_simple_tool_button_qta(
                parent=self.widget,
                icon_path="fa.copy",
                icon_size=QtCore.QSize(20, 20),
            ),
            layout=self.header_layout,
            alignment=Qt.AlignmentFlag.AlignTop,
            setup=lambda w, l: [
                w.setToolTip("Copy plot to clipboard"),
                w.clicked.connect(self.copy_plot),
            ],
        )

        self.zoom_button = widget_in_layout(
            widget=create_simple_tool_button_qta(
                parent=self.widget,
                icon_path="fa.search-plus",
                icon_size=QtCore.QSize(20, 20),
            ),
            layout=self.header_layout,
            alignment=Qt.AlignmentFlag.AlignTop,
            setup=lambda w, l: [
                w.setToolTip("Zoom plot"),
                w.clicked.connect(self.open_zoom),
            ],
        )

        self.image = widget_in_layout(
            widget=QLabelClickable(self.widget),
            layout=self.layout,
            setup=lambda w, l: [
                w.clicked.connect(lambda: self.activate_result(self.result_id, self.result_element_id)),
                w.doubleClicked.connect(self.open_zoom),
            ],
        )
        self.refresh()
        self.remove_focus(self.result_element_id)

    def open_zoom(self):
        # Select the plot (so its settings show) and open the zoom popup.
        self.activate_result(self.result_id, self.result_element_id)
        self.parent_class.set_display_element(self.result_element_id)

    def refresh(self):
        result_element = RESULTS[self.result_id].result_elements[self.result_element_id]
        # result_element = cast(result_element, PlotV2)
        buf = result_element.get_svg_buffer()

        renderer = QSvgRenderer()
        renderer.load(buf.read())
        buf.close()

        default_size = renderer.defaultSize()  # returns QSize
        if default_size.isEmpty():
            raise ValueError("SVG has no size information.")

        target_width = 265
        # Compute scaled height based on aspect ratio
        aspect_ratio = default_size.height() / default_size.width()
        target_height = int(target_width * aspect_ratio)
        target_size = QSize(target_width, target_height)

        pixmap = QPixmap(target_size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        self.image.setPixmap(pixmap)
        self.label.setText(result_element.plot_title.get_current_value())

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
                border_radius=Style.General.border_radius_medium,
            ),
        )

    def remove_focus(self, focused_result_element_id):
        logging.warning(f"Removing focus from {self.result_id} with element {focused_result_element_id}")
        assert focused_result_element_id is not None
        set_stylesheet(
            self.widget,
            css(
                border=Style.General.border_thin_unselected,
                border_radius=Style.General.border_radius_medium,
            ),
        )

    def copy_plot(self):
        self.copy_button.setIcon(qta.icon("fa.check", color=Style.Color.SimpleToolButton.value))
        result_element = RESULTS[self.result_id].result_elements[self.result_element_id]
        # Copy as HTML (title text + image) so the title can be edited after pasting.
        mime = QMimeData()
        mime.setHtml(result_element.get_html())
        QGuiApplication.clipboard().setMimeData(mime)
        QtCore.QTimer.singleShot(
            500, lambda: self.copy_button.setIcon(qta.icon("fa.copy", color=Style.Color.SimpleToolButton.value))
        )


class ZoomedPlotView(QFrame):
    """Minimal enlarged plot for the zoom popup: the figure at its native size with a
    small margin -- no title, buttons, or selectable border. Sizes to the plot."""

    def __init__(self, result_id, result_element_id, parent=None):
        super().__init__(parent)
        self.result_id = result_id
        self.result_element_id = result_element_id
        set_stylesheet(self, css(background="white"))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(0)
        self.image = QLabel(self)
        layout.addWidget(self.image)
        self.refresh()

    def refresh(self):
        result_element = RESULTS[self.result_id].result_elements[self.result_element_id]
        buf = result_element.get_svg_buffer()

        renderer = QSvgRenderer()
        renderer.load(buf.read())
        buf.close()

        size = renderer.defaultSize()
        if size.isEmpty():
            return

        pixmap = QPixmap(size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        self.image.setPixmap(pixmap)
        self.image.setFixedSize(size)
        self.adjustSize()
