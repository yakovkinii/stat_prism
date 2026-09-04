#  Copyright (C) 2023-2026  StatPrism Team
#  Balashevych A. K., Petrova N. V., Yakovkin I. I.
#
#  This file is part of StatPrism.
#
#  StatPrism is free software: you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  StatPrism is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  StatPrism.  If not, see <https://www.gnu.org/licenses/>.


import logging

import qtawesome as qta
from PySide6.QtCore import QMimeData, QSize, Qt, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QHBoxLayout, QLabel, QTextBrowser, QVBoxLayout, QWidget

from src.common.decorators import log_method
from src.common.progress import with_progress
from src.common.ui_constructor import create_simple_tool_button_qta
from src.data.data_manager import DATA_MANAGER
from src.main_area_panel.data_viewer.data_viewer import view_data_popup
from src.main_area_panel.result_display.base import BaseResultDisplay
from src.main_area_panel.result_display.elements.result_label import EditableTitle
from src.main_area_panel.result_display.plot_result_element import PlotResultElementDisplay, ZoomedPlotView
from src.main_area_panel.result_display.table_result_element import TableResultElementDisplay
from src.main_area_panel.show_in_main_area_popup import view_widget_in_popup
from src.pyside_ext.elements.utility.layout_helpers import empty_widget, widget_in_layout
from src.pyside_ext.elements.utility.primitive_elements import QWidgetClickable
from src.pyside_ext.flow_layout import FlowLayout
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.blueprint.registry import PanelRegistry
from src.side_area_panel.modules.common.inline_filter import (
    broken_filter_indices,
    describe_filter,
    filter_removed_positions,
    get_inline_filters,
    new_inline_filter,
)
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

        # Editable in place: clicking the title renames it; clicking beside it activates the card.
        self.label = widget_in_layout(
            widget=EditableTitle(parent=self.header_widget, result_id=result_id),
            layout=self.header_layout,
        )

        self.header_layout.addStretch()

        self.collapsed = False
        self.collapse_button = widget_in_layout(
            widget=create_simple_tool_button_qta(
                parent=self.header_widget,
                icon_path="mdi6.chevron-up",
                icon_size=QSize(20, 20),
            ),
            layout=self.header_layout,
            alignment=Qt.AlignmentFlag.AlignTop,
            setup=lambda w, l: [
                w.setToolTip("Collapse / expand"),
                w.clicked.connect(self.toggle_collapsed),
            ],
        )

        self.recalculate_button = widget_in_layout(
            widget=create_simple_tool_button_qta(
                parent=self.header_widget,
                icon_path="ph.arrows-clockwise-bold",
                icon_size=QSize(20, 20),
            ),
            layout=self.header_layout,
            alignment=Qt.AlignmentFlag.AlignTop,
            setup=lambda w, l: [
                w.setToolTip("Refresh"),
                w.clicked.connect(self.recalculate),
            ],
        )

        self.recalculate_full_button = widget_in_layout(
            widget=create_simple_tool_button_qta(
                parent=self.header_widget,
                icon_path="mdi6.restart",
                icon_size=QSize(20, 20),
            ),
            layout=self.header_layout,
            alignment=Qt.AlignmentFlag.AlignTop,
            setup=lambda w, l: [
                w.setToolTip("Reset & refresh"),
                w.clicked.connect(self.recalculate_full),
            ],
        )

        self.move_up_button = widget_in_layout(
            widget=create_simple_tool_button_qta(
                parent=self.header_widget,
                icon_path="mdi6.arrow-up",
                icon_size=QSize(20, 20),
            ),
            layout=self.header_layout,
            alignment=Qt.AlignmentFlag.AlignTop,
            setup=lambda w, l: [
                w.setToolTip("Move up"),
                w.clicked.connect(lambda: self.parent_class.move_data_analysis(self.result_id, -1)),
            ],
        )

        self.move_down_button = widget_in_layout(
            widget=create_simple_tool_button_qta(
                parent=self.header_widget,
                icon_path="mdi6.arrow-down",
                icon_size=QSize(20, 20),
            ),
            layout=self.header_layout,
            alignment=Qt.AlignmentFlag.AlignTop,
            setup=lambda w, l: [
                w.setToolTip("Move down"),
                w.clicked.connect(lambda: self.parent_class.move_data_analysis(self.result_id, 1)),
            ],
        )

        self.duplicate_button = widget_in_layout(
            widget=create_simple_tool_button_qta(
                parent=self.header_widget,
                icon_path="mdi6.content-duplicate",
                icon_size=QSize(20, 20),
            ),
            layout=self.header_layout,
            alignment=Qt.AlignmentFlag.AlignTop,
            setup=lambda w, l: [
                w.setToolTip("Duplicate this analysis"),
                w.clicked.connect(lambda: self.parent_class.duplicate_data_analysis(self.result_id)),
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

        self.add_filter_button = widget_in_layout(
            widget=create_simple_tool_button_qta(
                parent=self.header_widget,
                icon_path="mdi6.filter-plus-outline",
                icon_size=QSize(20, 20),
            ),
            layout=self.header_layout,
            alignment=Qt.AlignmentFlag.AlignTop,
            setup=lambda w, l: [
                w.setToolTip("Add an inline filter to this analysis"),
                w.clicked.connect(self._add_inline_filter),
            ],
        )

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

        self.info_button = widget_in_layout(
            widget=create_simple_tool_button_qta(
                parent=self.header_widget,
                icon_path="mdi6.information-outline",
                icon_size=QSize(20, 20),
            ),
            layout=self.header_layout,
            alignment=Qt.AlignmentFlag.AlignTop,
            setup=lambda w, l: [
                w.setToolTip("About this analysis (description & methodology)"),
                w.clicked.connect(self.show_description_popup),
            ],
        )
        self.description_popup = None

        # Per-analysis inline-filter block: a brief summary, one row per filter (rows-removed count
        # + eye / configure / delete), and an always-present Add button. Sits just under the title,
        # inside the body, so it collapses with the rest of the card.
        self._armed_delete_index = None
        self._active_filter_index = None  # the filter currently being configured (highlighted)
        self._filter_removed = {}  # filter index -> removed row positions (for the eye preview)
        self.filter_block, self.filter_block_layout = empty_widget(
            widget_class=QWidgetClickable,
            parent=self.widget,
            outer_layout=self.layout,
            inner_layout_class=QVBoxLayout,
            setup=lambda w, l: [
                l.setContentsMargins(2, 0, 20, 0),
                l.setSpacing(3),
                w.clicked.connect(lambda: self.activate_result(self.result_id, None)),
            ],
        )
        self.filter_rows_container, self.filter_rows_container_layout = empty_widget(
            widget_class=QWidget,
            parent=self.filter_block,
            outer_layout=self.filter_block_layout,
            inner_layout_class=QVBoxLayout,
            setup=lambda w, l: [l.setContentsMargins(0, 0, 0, 0), l.setSpacing(3)],
        )

        self.html_result_elements_container, self.html_result_elements_container_layout = empty_widget(
            widget_class=QWidgetClickable,
            parent=self.widget,
            outer_layout=self.layout,
            inner_layout_class=QVBoxLayout,
            setup=lambda w, l: [
                l.setSpacing(5),
                # Inset the table elements from the right so the strip beside them belongs to
                # the parent study card (clicking there selects the study, not the table).
                l.setContentsMargins(0, 0, 20, 0),
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
        self.display_popup = None
        self.element_display_objects = {}
        self.refresh()
        self.remove_focus(None)

    def toggle_collapsed(self):
        self.set_collapsed(not self.collapsed)

    def set_collapsed(self, collapsed: bool):
        """Collapse the study to its header (title + buttons) only, or expand it back."""
        self.collapsed = collapsed
        self.filter_block.setVisible(not collapsed)
        self.html_result_elements_container.setVisible(not collapsed)
        self.plot_result_elements_container.setVisible(not collapsed)
        self.collapse_button.setIcon(qta.icon("mdi6.chevron-down" if collapsed else "mdi6.chevron-up", color="#888"))

    def copy_all_elements(self):
        self.copy_button.setIcon(qta.icon("fa.check", color="#4CAF50"))

        result = RESULTS[self.result_id]
        full_html = "<html><body>"

        # Lead with the inline-filter summary so the copied output records what was filtered.
        filters_html = self._filters_html()
        if filters_html:
            full_html += filters_html + "<br><br>"

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
        self.set_stale(False)

    def set_stale(self, stale: bool):
        """Flag this study as out of date (manual-recalculate mode): tint the Refresh button
        an alarm color and set the result's needs_update. Reset when it is recalculated."""
        RESULTS[self.result_id].needs_update = stale
        self.recalculate_button.setIcon(qta.icon("ph.arrows-clockwise-bold", color="#e0a030" if stale else "#888"))

    def recalculate_full(self):
        # Drop the cache of user edits (axis titles, plot colors, table numbers...) so
        # every element rebuilds from its module defaults, then recalculate normally.
        RESULTS[self.result_id].old_result_elements = {}
        self.recalculate()

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

    def show_description_popup(self):
        """Show the study's description + methodology fine-print in a dimmed popup (closing
        on click outside), so it's available even when the study has results. Mirrors the
        plot-zoom popup."""
        description_html = getattr(RESULTS[self.result_id], "description", "") or ""

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        browser = QTextBrowser(container)
        browser.setOpenExternalLinks(True)
        browser.setHtml(description_html)
        container_layout.addWidget(browser)
        container.setFixedSize(QSize(620, 680))
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

    @log_method
    def set_display_element(self, result_element_id):
        # Zoom = show an enlarged copy of the plot in a popup that covers only the main
        # area (the settings panel stays visible/interactive), closing on click outside.
        self._close_zoom_popup()
        self.display_element_id = result_element_id
        self.display_object = ZoomedPlotView(
            result_id=self.result_id,
            result_element_id=result_element_id,
        )
        self.display_popup = view_widget_in_popup(
            parent=self.root_class.main_area_panel.widget,
            widget=self.display_object,
            handler_on_close=self._on_zoom_popup_closed,
        )

    @log_method
    def unset_display_element(self, result_element_id):
        self._close_zoom_popup()

    def _close_zoom_popup(self):
        """Close the zoom popup programmatically (refs cleared first so the popup's
        close doesn't re-enter)."""
        popup = self.display_popup
        self.display_popup = None
        self.display_object = None
        self.display_element_id = None
        if popup is not None:
            popup.close()

    def _on_zoom_popup_closed(self):
        """Called when the user clicks outside the plot (popup self-closes)."""
        self.display_popup = None
        self.display_object = None
        self.display_element_id = None

    def refresh_element(self, result_element_id):
        if result_element_id in self.element_display_objects:
            self.element_display_objects[result_element_id].refresh()
            # Keep the zoom popup live while settings change, resizing it with the plot.
            if result_element_id == self.display_element_id and self.display_object is not None:
                self.display_object.refresh()
                if self.display_popup is not None:
                    self.display_popup.recenter_content()
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

    def _base_data(self):
        """The analysis's input data BEFORE inline filters (for counts / previews). None on error."""
        result = RESULTS[self.result_id]
        source = getattr(result.config, "data_source", None) or "Auto"
        DATA_MANAGER._apply_inline = False
        try:
            return DATA_MANAGER.get_data_from_data_label(data_label=source, current_result_id=self.result_id)
        except Exception:
            return None
        finally:
            DATA_MANAGER._apply_inline = True

    def _filter_rows_info(self):
        """Per-filter display info. Filters combine with AND; each row reports the ADDITIONAL rows
        it removes beyond the ones the earlier filters already removed (marginal), so the marginals
        sum to the total. Returns (info list, base data or None, total rows removed)."""
        filters = get_inline_filters(RESULTS[self.result_id])
        base = self._base_data()
        broken = set(broken_filter_indices(base, filters)) if base is not None else set()
        cumulative = set()
        info = []
        for index, cfg in enumerate(filters):
            removed = set(filter_removed_positions(base, cfg)) if base is not None else set()
            marginal = sorted(removed - cumulative)
            cumulative |= removed
            info.append({"index": index, "cfg": cfg, "marginal": marginal, "broken": index in broken})
        return info, base, len(cumulative)

    def refresh_filters(self):
        """Rebuild the inline-filter block from the analysis's stored filters."""
        while self.filter_rows_container_layout.count():
            item = self.filter_rows_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._filter_removed = {}

        info, base, _total_removed = self._filter_rows_info()
        for entry in info:
            self._build_filter_row(entry, base)

    def _build_filter_row(self, entry, base):
        index, cfg, marginal, is_broken = entry["index"], entry["cfg"], entry["marginal"], entry["broken"]
        self._filter_removed[index] = marginal

        # The whole row is clickable to open the filter's configuration (there is no separate
        # configure button); the eye and delete buttons handle their own clicks.
        row, row_layout = empty_widget(
            widget_class=QWidgetClickable,
            parent=self.filter_rows_container,
            outer_layout=self.filter_rows_container_layout,
            inner_layout_class=QHBoxLayout,
            setup=lambda w, l: [
                l.setContentsMargins(4, 2, 4, 2),
                l.setSpacing(6),
                w.setToolTip("Click to configure this filter"),
                w.clicked.connect(lambda i=index: self._configure_filter(i)),
            ],
        )
        # Styled like a result element: thin border, highlighted while this filter is being
        # configured. A broken filter (its column is gone) gets a red outline instead.
        if is_broken:
            border = "1px solid red"
        elif index == self._active_filter_index:
            border = Style.General.border_thin_selected_element
        else:
            border = Style.General.border_thin_unselected
        set_stylesheet(row, css(border=border, border_radius="5px"))

        text = describe_filter(cfg)
        label_text = f"{text}: column missing" if is_broken else f"{text}: {len(marginal)} rows removed"
        label = widget_in_layout(widget=QLabel(label_text, row), layout=row_layout)
        set_stylesheet(
            label,
            css(color=(Style.Color.Danger if is_broken else Style.Color.Text), font_size=Style.FontSize.smaller),
        )
        row_layout.addStretch()

        eye = widget_in_layout(
            widget=create_simple_tool_button_qta(parent=row, icon_path="mdi6.eye-outline", icon_size=QSize(18, 18)),
            layout=row_layout,
            setup=lambda w, l: [
                w.setToolTip("Preview the rows this filter removes"),
                w.clicked.connect(lambda i=index: self._preview_filter(i)),
            ],
        )
        eye.setEnabled(base is not None and not is_broken)
        delete = widget_in_layout(
            widget=create_simple_tool_button_qta(parent=row, icon_path="mdi6.delete-outline", icon_size=QSize(18, 18)),
            layout=row_layout,
        )
        armed = self._armed_delete_index == index
        delete.setIcon(
            qta.icon("mdi6.delete-alert" if armed else "mdi6.delete-outline", color="#AF4C50" if armed else "#888")
        )
        delete.setToolTip("Delete (click again to confirm)")
        delete.clicked.connect(lambda _=False, i=index, b=delete: self._delete_filter_clicked(i, b))

    def _filters_html(self):
        """HTML summary of the inline filters, for the copied output (empty when none)."""
        info, _base, _total_removed = self._filter_rows_info()
        if not info:
            return ""
        lines = ["<b>Filters</b>"]
        for entry in info:
            condition = describe_filter(entry["cfg"])
            if entry["broken"]:
                lines.append(f"{condition}: column missing")
            else:
                lines.append(f"{condition}: {len(entry['marginal'])} rows removed")
        return "<br>".join(lines)

    def _add_inline_filter(self):
        result = RESULTS[self.result_id]
        filters = get_inline_filters(result)
        source = getattr(result.config, "data_source", None) or "Auto"
        filters.append(new_inline_filter(source))
        self.root_class.mark_dirty()
        # A fresh (unconfigured) filter removes nothing, so no recompute is needed yet -- just show
        # the new row and open it for configuration.
        self.refresh_filters()
        self._configure_filter(len(filters) - 1)

    def _configure_filter(self, filter_index):
        panel_index = PanelRegistry.INLINE_FILTER.settings_stacked_widget_index
        self.root_class.settings_panel.panels[panel_index].configure(self.result_id, filter_index)
        self.root_class.action_activate_panel_by_index(panel_index)
        self.root_class.main_area_panel.update_focus(self.result_id, None)
        # Highlight the row being configured (set after update_focus, which clears it via remove_focus).
        self._active_filter_index = filter_index
        self.refresh_filters()

    def _preview_filter(self, filter_index):
        base = self._base_data()
        if base is None:
            return
        view_data_popup(self.widget, base, highlight_rows=self._filter_removed.get(filter_index, []))

    def _delete_filter_clicked(self, filter_index, button):
        if self._armed_delete_index == filter_index:
            self._armed_delete_index = None
            self._do_delete_filter(filter_index)
        else:
            self._armed_delete_index = filter_index
            button.setIcon(qta.icon("mdi6.delete-alert", color="#AF4C50"))
            QTimer.singleShot(1500, lambda i=filter_index: self._disarm_delete(i))

    def _disarm_delete(self, filter_index):
        if self._armed_delete_index == filter_index:
            self._armed_delete_index = None
            self.refresh_filters()

    def _do_delete_filter(self, filter_index):
        filters = get_inline_filters(RESULTS[self.result_id])
        if 0 <= filter_index < len(filters):
            del filters[filter_index]
        # Removing a configured filter changes the results -> recompute the analysis (this also
        # refreshes the card, rebuilding the filter block).
        self.recalculate()

    def refresh(self):
        # A full rebuild invalidates any zoomed copy; close the popup first.
        self._close_zoom_popup()
        self.label.refresh()  # in case a reset reverted the title to the module type name
        self.refresh_filters()
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
            # Leaving the study also ends any inline-filter configuration, so drop the highlight.
            if self._active_filter_index is not None:
                self._active_filter_index = None
                self.refresh_filters()
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
