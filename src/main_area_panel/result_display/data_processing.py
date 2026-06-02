#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import logging

from PySide6 import QtCore
from PySide6.QtCore import QSize, QTimer
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QPushButton, QVBoxLayout

from src.common.decorators import log_method
from src.common.ui_constructor import create_tool_button_qta, create_simple_tool_button_qta
from src.main_area_panel.data_viewer.data_viewer import view_data_popup
from src.main_area_panel.result_display.base import BaseResultDisplay
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
import qtawesome as qta

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

        self.export_button = widget_in_layout(
            widget=create_simple_tool_button_qta(
                parent=self.header_widget,
                icon_path="mdi6.microsoft-excel",
                icon_size=QSize(20, 20),
            ),
            layout=self.header_layout,
            alignment=Qt.AlignmentFlag.AlignTop,
            setup=lambda w, l: [
                w.setToolTip("Export to Excel"),
                w.clicked.connect(self.export_to_excel),
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
                w.setToolTip("Delete"),
                w.clicked.connect(self.delete),
            ],
        )
        self.deleting = False
        self.deleted = False

        self.body_widget, self.body_layout = empty_widget(
            widget_class=QWidgetClickable,
            parent=self.widget,
            outer_layout=self.layout,
            inner_layout_class=QHBoxLayout,
            setup=lambda w, l: [
                w.clicked.connect(lambda: self.activate_result(self.result_id, None)),
                l.setContentsMargins(10, 10, 5, 5),
                l.setSpacing(10),
            ],
        )

        self.popup_button = widget_in_layout(
            widget=create_tool_button_qta(
                parent=self.body_widget,
                icon_path="mdi.table-eye",
                icon_size=QtCore.QSize(50, 50),
            ),
            layout=self.body_layout,
            alignment=Qt.AlignmentFlag.AlignTop,
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

        self.info = widget_in_layout(
            widget=QLabelClickable(self.body_widget),
            layout=self.body_layout,
            setup=lambda w, l: [
                w.setWordWrap(True),
                w.clicked.connect(lambda: self.activate_result(self.result_id, None)),
            ],
        )

        # Large enable/disable toggle for toggleable results (e.g. the Filter module),
        # flush to the right of the view-data button and description.
        self.toggle_button = None
        if getattr(RESULTS[self.result_id], "toggleable", False):
            self.body_layout.addStretch()
            self.toggle_button = widget_in_layout(
                widget=QPushButton(self.body_widget),
                layout=self.body_layout,
                alignment=Qt.AlignmentFlag.AlignTop,
                setup=lambda w, l: [
                    w.setMinimumHeight(40),
                    w.setCursor(Qt.CursorShape.PointingHandCursor),
                    w.clicked.connect(self.toggle_enabled),
                ],
            )

        self.refresh()
        self.remove_focus(None)

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

    def refresh(self):
        result = RESULTS[self.result_id]
        self.body_widget.show()
        self.info.setText(result.description)
        self._update_toggle()

    def _update_toggle(self):
        if self.toggle_button is None:
            return
        enabled = getattr(RESULTS[self.result_id].config, "enabled", True)
        if enabled:
            self.toggle_button.setText("Enabled")
            set_stylesheet(self.toggle_button, css(background_color="#cdeacd", font_size=Style.FontSize.regular))
        else:
            self.toggle_button.setText("Disabled")
            set_stylesheet(self.toggle_button, css(background_color="#e0e0e0", font_size=Style.FontSize.regular))

    def toggle_enabled(self):
        result = RESULTS[self.result_id]
        result.config.enabled = not getattr(result.config, "enabled", True)
        # Round-trips enabled through the side panel (configure pushes it into the
        # hidden checkbox, recalculate reads it back) and refreshes this card.
        self.recalculate()

    def recalculate(self):
        panel = self.root_class.settings_panel.panels[RESULTS[self.result_id].settings_panel_index]
        panel.configure(self.result_id)
        panel.recalculate()

    def export_to_excel(self):
        data = RESULTS[self.result_id].data
        if data is None or data.n_columns() == 0:
            logging.info("No data to export")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self.widget,
            "Export to Excel",
            "",
            "Excel files (*.xlsx)",
        )
        if not file_path:
            return
        if not file_path.endswith(".xlsx"):
            file_path += ".xlsx"

        try:
            data.get_dataframe().to_excel(file_path, index=False)
        except Exception as e:
            logging.error(f"Failed to export data to Excel: {e}")

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