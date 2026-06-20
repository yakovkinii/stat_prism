#  Copyright (c) 2023 StatPrism Team. All rights reserved.
from PySide6 import QtCore
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout

from src.common.decorators import log_method
from src.common.ui_constructor import create_simple_tool_button_qta, create_tool_button_qta
from src.main_area_panel.data_viewer.data_viewer import view_data_popup
from src.main_area_panel.result_display.base import BaseResultDisplay
from src.main_area_panel.result_display.export import export_data_to_excel
from src.main_area_panel.result_display.elements.result_label import ResultLabel
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


class RawDataResultDisplay(BaseResultDisplay):
    def __init__(self, parent_widget, parent_class, root_class, label_text: str, result_id):
        super().__init__(parent_widget, parent_class, root_class)
        self.result_id = result_id

        self.widget, self.layout = empty_widget(
            widget_class=QWidgetClickable,
            parent=self.parent_widget,
            inner_layout_class=QVBoxLayout,
            setup=lambda w, l: [
                l.setContentsMargins(8, 2, 8, 2),
                l.setSpacing(0),
                w.clicked.connect(lambda: self.activate_result(self.result_id, None)),
            ],
        )

        # One compact band: [view data] [title + info].
        self.body_widget, self.body_layout = empty_widget(
            widget_class=QWidgetClickable,
            parent=self.widget,
            outer_layout=self.layout,
            inner_layout_class=QHBoxLayout,
            setup=lambda w, l: [
                w.clicked.connect(lambda: self.activate_result(self.result_id, None)),
                l.setContentsMargins(4, 2, 4, 2),
                l.setSpacing(8),
            ],
        )

        self.popup_button = widget_in_layout(
            widget=create_tool_button_qta(
                parent=self.body_widget,
                icon_path="mdi.table-eye",
                icon_size=QtCore.QSize(50, 50),
            ),
            layout=self.body_layout,
            alignment=Qt.AlignmentFlag.AlignVCenter,
            setup=lambda w, l: [
                w.setToolTip("View Data"),
                w.clicked.connect(
                    lambda: view_data_popup(
                        parent=self.root_class.main_area_panel.widget,
                        data=RESULTS[self.result_id].data,
                    )
                ),
            ],
        )

        # Title and description stacked next to the view button (no separate row).
        self.text_widget, self.text_layout = empty_widget(
            widget_class=QWidgetClickable,
            parent=self.body_widget,
            inner_layout_class=QVBoxLayout,
            setup=lambda w, l: [
                l.setContentsMargins(0, 0, 0, 0),
                l.setSpacing(0),
                w.clicked.connect(lambda: self.activate_result(self.result_id, None)),
            ],
        )
        self.body_layout.addWidget(self.text_widget, 1)

        self.label = widget_in_layout(
            widget=ResultLabel(parent=self.text_widget, label_text=label_text),
            layout=self.text_layout,
            setup=lambda w, l: [w.clicked.connect(lambda: self.activate_result(self.result_id, None))],
        )

        self.info = widget_in_layout(
            widget=QLabelClickable(self.text_widget),
            layout=self.text_layout,
            setup=lambda w, l: [
                w.setWordWrap(True),
                w.clicked.connect(lambda: self.activate_result(self.result_id, None)),
            ],
        )

        # Action buttons, top-right -- matches the data-processing cards' layout.
        self.actions_widget, self.actions_layout = empty_widget(
            widget_class=QWidgetClickable,
            parent=self.body_widget,
            inner_layout_class=QHBoxLayout,
            setup=lambda w, l: [
                l.setContentsMargins(0, 0, 0, 0),
                l.setSpacing(2),
            ],
        )
        self.body_layout.addWidget(self.actions_widget, alignment=Qt.AlignmentFlag.AlignTop)

        self.export_button = widget_in_layout(
            widget=create_simple_tool_button_qta(
                parent=self.actions_widget,
                icon_path="mdi6.microsoft-excel",
                icon_size=QtCore.QSize(20, 20),
            ),
            layout=self.actions_layout,
            setup=lambda w, l: [
                w.setToolTip("Export to Excel"),
                w.clicked.connect(lambda: export_data_to_excel(self.widget, RESULTS[self.result_id].data)),
            ],
        )

        self.refresh()
        self.remove_focus(None)

    def refresh(self):
        result = RESULTS[self.result_id]
        config = result.config
        if result.data is None:
            return self.body_widget.hide()
        self.body_widget.show()
        self.info.setText(
            f"File: {config.path} \n"
            f"Time: {config.timestamp} \n"
            f"{result.data.n_rows()} rows × {result.data.n_columns()} columns"
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
                border_radius=Style.General.border_radius_medium,
            ),
        )

    def remove_focus(self, result_element_id):
        set_stylesheet(
            self.widget,
            css(
                background_color=Style.Color.Background,
                border=Style.General.border_thin_unselected,
                border_left=Style.General.border_thick_unselected,
                border_radius=Style.General.border_radius_medium,
            ),
        )
