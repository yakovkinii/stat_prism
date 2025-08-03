#  Copyright (c) 2023 StatPrism Team. All rights reserved.
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QLabel, QVBoxLayout

from src.common.elements.utility.layout_helpers import empty_widget, widget_in_layout
from src.common.result.registry import RESULTS
from src.main_area_panel.result_display.base import BaseResultDisplay
from src.main_area_panel.result_display.elements.result_element_label import ResultElementLabel
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet


class PlotResultElementDisplay(BaseResultDisplay):
    def __init__(self, parent_widget, parent_class, root_class, label_text: str, result_id, result_element_id):
        super().__init__(parent_widget, parent_class, root_class)
        self.result_id = result_id
        self.result_element_id = result_element_id

        self.widget, self.layout = empty_widget(
            parent=self.parent_widget,
            inner_layout_class=QVBoxLayout,
        )
        set_stylesheet(self.widget, css(background_color=Style.Color.Background))

        self.label = widget_in_layout(
            widget=ResultElementLabel(parent=self.widget, label_text=label_text),
            layout=self.layout,
        )

        self.image = widget_in_layout(
            widget=QLabel(self.widget),
            layout=self.layout,
        )
        self.refresh()

    def refresh(self):
        buf = RESULTS[self.result_id].result_elements[self.result_element_id].get_buffer()

        renderer = QSvgRenderer()
        renderer.load(buf.read())

        # Set output size (adjust as needed)
        target_width = 600
        default_size = renderer.defaultSize()  # returns QSize
        if default_size.isEmpty():
            raise ValueError("SVG has no size information.")

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
