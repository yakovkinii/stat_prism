#  Copyright (c) 2023 StatPrism Team. All rights reserved.
from PySide6 import QtCore
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout

from src.common.decorators import log_method
from src.common.ui_constructor import create_tool_button_qta
from src.data_viewer.data_viewer import view_data_popup
from src.main_area_panel.result_display.base import BaseResultDisplay
from src.main_area_panel.result_display.elements.result_label import ResultLabel
from src.modules.common.result.registry import RESULTS
from src.pyside_ext.elements.utility.layout_helpers import empty_widget, widget_in_layout
from src.pyside_ext.elements.utility.primitive_elements import QWidgetClickable
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet


class DataProcessingResultDisplay(BaseResultDisplay):
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

        self.popup_button = widget_in_layout(
            widget=create_tool_button_qta(
                parent=self.widget,
                icon_path="mdi.table-eye",
                icon_size=QtCore.QSize(40, 40),
            ),
            layout=self.header_layout,
            alignment=Qt.AlignmentFlag.AlignTop,
            setup=lambda w, l: [
                w.setToolTip("View Data"),
                w.clicked.connect(
                    lambda: view_data_popup(
                        root_class=self.root_class,
                        data=RESULTS[self.result_id].config.data,
                    )
                ),
            ],
        )

        self.label = widget_in_layout(
            widget=ResultLabel(parent=self.header_widget, label_text=label_text),
            layout=self.header_layout,
            setup=lambda w, l: [w.clicked.connect(lambda: self.activate_result(self.result_id, None))],
        )

    @log_method
    def activate_result(self, result_id, result_element_id):
        self.parent_class.activate_result(result_id, result_element_id)

    def set_focus(self, result_element_id):
        set_stylesheet(
            self.widget,
            css(
                background_color=Style.Color.Background,
                border=Style.General.border_thin_selected,
                border_left=Style.General.border_thick_selected,
                border_radius="5px",
            ),
        )

    def remove_focus(self, result_element_id):
        set_stylesheet(
            self.widget,
            css(
                background_color=Style.Color.Background,
                border=Style.General.border_thin_unselected,
                border_left=Style.General.border_thick_unselected,
                border_radius="5px",
            ),
        )
