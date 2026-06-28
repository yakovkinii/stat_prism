#  Copyright (c) 2023 StatPrism Team. All rights reserved.
from PySide6 import QtCore
from PySide6.QtCore import QSize, QTimer
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QTextBrowser, QVBoxLayout, QWidget

from src.common.decorators import log_method
from src.main_area_panel.result_display.export import export_data_to_excel
from src.common.ui_constructor import create_tool_button_qta, create_simple_tool_button_qta
from src.main_area_panel.data_viewer.data_viewer import view_data_popup
from src.main_area_panel.show_in_main_area_popup import view_widget_in_popup
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
from src.pyside_ext.markup import HTML, css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.pyside_ext.elements.toggle_switch import ToggleSwitch
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
                l.setContentsMargins(8, 2, 8, 2),
                l.setSpacing(0),
                w.clicked.connect(lambda: self.activate_result(self.result_id, None)),
            ],
        )

        # One compact band: [view data] [title + info] [actions] [toggle].
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
                icon_path="mdi6.eye-outline",
                icon_size=QtCore.QSize(50, 50),
            ),
            layout=self.body_layout,
            alignment=Qt.AlignmentFlag.AlignVCenter,
            setup=lambda w, l: [
                w.setToolTip("View Data"),
                w.clicked.connect(self._view_data),
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
            setup=lambda w, l: [
                w.clicked.connect(lambda: self.activate_result(self.result_id, None)),
                w.setFont(Style.font_study_title),
                set_stylesheet(w, css(color=Style.Color.TitleBrand)),
            ],
        )

        self.info = widget_in_layout(
            widget=QLabelClickable(self.text_widget),
            layout=self.text_layout,
            setup=lambda w, l: [
                w.setWordWrap(True),
                w.clicked.connect(lambda: self.activate_result(self.result_id, None)),
            ],
        )

        # Collapsed view: the fine-print sits to the right of the title on one line, never
        # wrapping -- any overflow is simply clipped (Ignored size policy lets the layout
        # give it only the leftover width).
        self.info_inline = widget_in_layout(
            widget=QLabelClickable(self.body_widget),
            layout=self.body_layout,
            setup=lambda w, l: [
                w.setWordWrap(False),
                w.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred),
                set_stylesheet(w, css(color=Style.Color.SecondaryText, font_size=Style.FontSize.smallest)),
                w.clicked.connect(lambda: self.activate_result(self.result_id, None)),
            ],
        )

        # Enable/disable toggle for toggleable results (e.g. the Filter module). It sits to
        # the left of the small action icons in the top row.
        self.toggle_button = None
        if getattr(RESULTS[self.result_id], "toggleable", False):
            self.toggle_button = widget_in_layout(
                widget=ToggleSwitch(self.body_widget),
                layout=self.body_layout,
                alignment=Qt.AlignmentFlag.AlignVCenter,
                setup=lambda w, l: [
                    w.setToolTip("Enable / disable this step"),
                    w.toggled.connect(self.toggle_enabled),
                ],
            )

        # Action buttons, top-right.
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

        self.collapsed = True
        self.collapse_button = widget_in_layout(
            widget=create_simple_tool_button_qta(
                parent=self.actions_widget,
                icon_path="mdi6.chevron-down",
                icon_size=QSize(20, 20),
            ),
            layout=self.actions_layout,
            setup=lambda w, l: [
                w.setToolTip("Collapse / expand"),
                w.clicked.connect(self.toggle_collapsed),
            ],
        )

        self.move_up_button = widget_in_layout(
            widget=create_simple_tool_button_qta(
                parent=self.actions_widget,
                icon_path="mdi6.arrow-up",
                icon_size=QSize(20, 20),
            ),
            layout=self.actions_layout,
            setup=lambda w, l: [
                w.setToolTip("Move up"),
                w.clicked.connect(lambda: self.parent_class.move_data_processing(self.result_id, -1)),
            ],
        )

        self.move_down_button = widget_in_layout(
            widget=create_simple_tool_button_qta(
                parent=self.actions_widget,
                icon_path="mdi6.arrow-down",
                icon_size=QSize(20, 20),
            ),
            layout=self.actions_layout,
            setup=lambda w, l: [
                w.setToolTip("Move down"),
                w.clicked.connect(lambda: self.parent_class.move_data_processing(self.result_id, 1)),
            ],
        )

        self.recalculate_button = widget_in_layout(
            widget=create_simple_tool_button_qta(
                parent=self.actions_widget,
                icon_path="ph.arrows-clockwise-bold",
                icon_size=QSize(20, 20),
            ),
            layout=self.actions_layout,
            setup=lambda w, l: [
                w.setToolTip("Recalculate"),
                w.clicked.connect(self.recalculate),
            ],
        )

        self.info_button = widget_in_layout(
            widget=create_simple_tool_button_qta(
                parent=self.actions_widget,
                icon_path="mdi6.information-outline",
                icon_size=QSize(20, 20),
            ),
            layout=self.actions_layout,
            setup=lambda w, l: [
                w.setToolTip("About this step (description & methodology)"),
                w.clicked.connect(self.show_description_popup),
            ],
        )
        self.description_popup = None

        self.export_button = widget_in_layout(
            widget=create_simple_tool_button_qta(
                parent=self.actions_widget,
                icon_path="mdi6.microsoft-excel",
                icon_size=QSize(20, 20),
            ),
            layout=self.actions_layout,
            setup=lambda w, l: [
                w.setToolTip("Export to Excel"),
                w.clicked.connect(self.export_to_excel),
            ],
        )

        self.delete_button = widget_in_layout(
            widget=create_simple_tool_button_qta(
                parent=self.actions_widget,
                icon_path="mdi6.delete",
                icon_size=QSize(20, 20),
            ),
            layout=self.actions_layout,
            setup=lambda w, l: [
                w.setToolTip("Delete"),
                w.clicked.connect(self.delete),
            ],
        )
        self.deleting = False
        self.deleted = False

        self.refresh()
        self.set_collapsed(True)
        self.remove_focus(None)

    def toggle_collapsed(self):
        self.set_collapsed(not self.collapsed)

    def set_collapsed(self, collapsed: bool):
        """Collapsed: title + one-line fine-print on a single short band. Expanded: the
        full (wrapping) fine-print below the title and a larger View-Data button."""
        self.collapsed = collapsed
        self.info.setVisible(not collapsed)
        self.info_inline.setVisible(collapsed)
        # Collapsed -> title hugs its text and the inline fine-print absorbs the leftover
        # width (clipping overflow). Expanded -> the text column grows so the block fine-
        # print can wrap.
        self.body_layout.setStretchFactor(self.text_widget, 0 if collapsed else 1)
        self.body_layout.setStretchFactor(self.info_inline, 1 if collapsed else 0)
        # Keep the View-Data button the same width when collapsed, only shorter (a wide,
        # flat button) rather than shrinking it to a small square.
        self.popup_button.setFixedSize(QSize(56, 30) if collapsed else QSize(56, 56))
        self.popup_button.setIconSize(QSize(28, 28) if collapsed else QSize(50, 50))
        self.collapse_button.setIcon(
            qta.icon("mdi6.chevron-down" if collapsed else "mdi6.chevron-up", color="#888")
        )

    def _view_data(self):
        """Open the data preview. For a step that tracks removed rows (Filter), show the full
        data with the removed rows in red; otherwise show the step's output as-is."""
        result = RESULTS[self.result_id]
        full_data = getattr(result, "full_data", None)
        removed = getattr(result, "removed_positions", None)
        if full_data is not None and full_data.n_columns() > 0 and removed:
            view_data_popup(
                parent=self.root_class.main_area_panel.widget,
                data=full_data,
                highlight_rows=removed,
            )
        else:
            view_data_popup(
                parent=self.root_class.main_area_panel.widget,
                data=result.data,
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

    def refresh(self):
        result = RESULTS[self.result_id]
        self.body_widget.show()
        description = result.description
        data = result.data
        inline = ""
        if data is not None:
            shape = f"{data.n_rows()} rows &times; {data.n_columns()} columns"
            description = f"{description}<br>{shape}" if description else shape
            # One-line version for the collapsed band: full text, line breaks become " | "
            # and the HTML entity becomes a real "×" (the inline label renders as plain text).
            inline = description.replace("<br>", " | ").replace("&times;", "×")
        # A validation / status message (e.g. "Select a column") leads the summary in red so
        # the user sees why a step produced no change.
        error = getattr(result, "error_message", "")
        if error:
            error_html = HTML.div(HTML.bold(error), color=Style.Color.Danger.value)
            description = f"{error_html}<br>{description}" if description else error_html
            inline = f"⚠ {error} | {inline}" if inline else f"⚠ {error}"
        self.info.setText(description)
        self.info_inline.setText(inline)
        self._update_toggle()

    def _update_toggle(self):
        if self.toggle_button is None:
            return
        enabled = getattr(RESULTS[self.result_id].config, "enabled", True)
        # Reflect the state without re-triggering toggle_enabled.
        self.toggle_button.blockSignals(True)
        self.toggle_button.setChecked(bool(enabled))
        self.toggle_button.blockSignals(False)

    def toggle_enabled(self, checked: bool):
        result = RESULTS[self.result_id]
        result.config.enabled = bool(checked)
        # Round-trips enabled through the side panel (configure pushes it into the
        # hidden checkbox, recalculate reads it back) and refreshes this card.
        self.recalculate()

    def show_description_popup(self):
        """Show this step's methodology (falling back to its live summary) in a dimmed
        popup that closes on click-outside -- mirrors the analysis cards' info button."""
        result = RESULTS[self.result_id]
        html = getattr(result, "methodology", "") or getattr(result, "description", "") or ""

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        browser = QTextBrowser(container)
        browser.setOpenExternalLinks(True)
        browser.setHtml(html)
        container_layout.addWidget(browser)
        container.setFixedSize(QSize(560, 520))
        set_stylesheet(
            browser,
            css(
                background_color=Style.Color.BackgroundElevated,
                color=Style.Color.Text,
                border=Style.General.border,
                border_color=Style.Color.BorderElevated,
                border_radius="8px",
                padding="16px",
            ),
        )

        self._close_description_popup()
        self.description_popup = view_widget_in_popup(
            parent=self.root_class.main_area_panel.widget,
            widget=container,
            handler_on_close=self._on_description_popup_closed,
        )

    def _close_description_popup(self):
        popup = self.description_popup
        self.description_popup = None
        if popup is not None:
            popup.close()

    def _on_description_popup_closed(self):
        self.description_popup = None

    def recalculate(self):
        panel = self.root_class.settings_panel.panels[RESULTS[self.result_id].settings_panel_index]
        panel.configure(self.result_id)
        panel.recalculate()
        self.set_stale(False)

    def set_stale(self, stale: bool):
        """Flag this study as out of date (manual-recalculate mode): tint the Refresh button
        an alarm colour and set the result's needs_update. Reset when it is recalculated."""
        RESULTS[self.result_id].needs_update = stale
        self.recalculate_button.setIcon(
            qta.icon("ph.arrows-clockwise-bold", color="#e0a030" if stale else "#888")
        )

    def export_to_excel(self):
        export_data_to_excel(self.widget, RESULTS[self.result_id].data)

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