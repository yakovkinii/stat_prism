#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import logging
from typing import TYPE_CHECKING

from PySide6 import QtWidgets
from PySide6.QtWidgets import QVBoxLayout

from src.common.decorators import log_method
from src.data.data_manager import DATA_MANAGER
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
from src.side_area_panel.blueprint.registry import PanelRegistry
from src.side_area_panel.modules.common.result.registry import RESULTS, get_unique_result_id

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
                l.setSpacing(2),
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
                l.setContentsMargins(10, 0, 20, 0),
                l.setSpacing(4),
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
                l.setContentsMargins(10, 0, 20, 0),
                l.setSpacing(4),
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
                l.setContentsMargins(10, 0, 20, 0),
                l.setSpacing(4),
                w.clicked.connect(lambda: self.activate_result(None, None)),
            ],
        )

        self.layout.addStretch()

        self.focused_result_id = None
        self.focused_result_element_id = None
        self._cascading = False
        # When True, a data-processing change recomputes every dependent study immediately.
        # When False (default), dependents are only flagged stale (Refresh turns an alarm
        # colour) until the user recalculates. Persisted in statprism.ini; toggled from
        # Settings ▸ Auto-recalculate.
        from src.common.ui_theme import read_auto_recalculate

        self.auto_recalculate = read_auto_recalculate(default=False)

        self.raw_data_objects = {}
        self.data_processing_objects = {}
        self.data_analysis_objects = {}

    def clear_all(self):
        """Tear down every result card and forget all results / chain state. Used when
        opening a project or starting a new one, so nothing from the previous session
        lingers in the UI or the registries."""
        for objects, layout in (
            (self.data_analysis_objects, self.data_analysis_container_layout),
            (self.data_processing_objects, self.data_processing_container_layout),
            (self.raw_data_objects, self.raw_data_container_layout),
        ):
            for obj in objects.values():
                layout.removeWidget(obj.widget)
                obj.widget.setParent(None)
                obj.widget.deleteLater()
            objects.clear()

        self.focused_result_id = None
        self.focused_result_element_id = None

        RESULTS.clear()
        DATA_MANAGER.reset()

    def _recompute_result(self, result_id):
        panel = self.root_class.settings_panel.panels[RESULTS[result_id].settings_panel_index]
        panel.configure(result_id)
        panel.recalculate()

    def cascade_update(self, source_result_id):
        """When a data-processing / raw-data result changes, recompute every
        downstream data-processing study (in chain order) and every data-analysis
        study. Analysis edits do not propagate (they are leaves)."""
        if self._cascading or source_result_id not in DATA_MANAGER.data_chain:
            return
        if not self.auto_recalculate:
            # Manual mode: don't recompute, just flag the dependents stale.
            self._flag_dependents_stale(source_result_id)
            return
        self._cascading = True
        try:
            for result_id in self._dependent_ids(source_result_id):
                self._recompute_result(result_id)
        finally:
            self._cascading = False

    def _dependent_ids(self, source_result_id):
        """Downstream data-processing studies (in chain order) + every analysis study."""
        chain = list(DATA_MANAGER.data_chain)
        start = chain.index(source_result_id) + 1
        ids = [rid for rid in chain[start:] if rid in self.data_processing_objects]
        ids += list(self.data_analysis_objects)
        return ids

    def _flag_dependents_stale(self, source_result_id):
        """Mark every dependent study as needing recalculation and turn its Refresh button
        an alarm colour, without recomputing (manual / auto-recalculate-off mode)."""
        for result_id in self._dependent_ids(source_result_id):
            RESULTS[result_id].needs_update = True
            obj = self.data_processing_objects.get(result_id) or self.data_analysis_objects.get(result_id)
            if obj is not None and hasattr(obj, "set_stale"):
                obj.set_stale(True)

    def recompute_all(self):
        """Recompute every data-processing study (chain order) and every analysis."""
        if self._cascading:
            return
        self._cascading = True
        try:
            for result_id in list(DATA_MANAGER.data_chain):
                if result_id in self.data_processing_objects:
                    self._recompute_result(result_id)
            for result_id in list(self.data_analysis_objects):
                self._recompute_result(result_id)
        finally:
            self._cascading = False
        # Everything is now up to date -- clear any stale (alarm) flags.
        for obj in list(self.data_processing_objects.values()) + list(self.data_analysis_objects.values()):
            if hasattr(obj, "set_stale"):
                obj.set_stale(False)

    def collapse_all(self):
        """Collapse every study card (raw data, data-processing, analysis) to its header."""
        for objects in (self.raw_data_objects, self.data_processing_objects, self.data_analysis_objects):
            for obj in objects.values():
                if hasattr(obj, "set_collapsed"):
                    obj.set_collapsed(True)

    def add_raw_data(self, result_id):
        raw_data_object = RawDataResultDisplay(
            parent_widget=self.raw_data_widget_container,
            parent_class=self,
            root_class=self.root_class,
            label_text=RESULTS[result_id].title + f" [Data{result_id}]",
            result_id=result_id,
        )
        self.raw_data_objects[result_id] = raw_data_object
        self.raw_data_container_layout.addWidget(raw_data_object.widget)
        self.root_class.mark_dirty()

    def add_data_processing(self, result_id):
        data_processing_object = DataProcessingResultDisplay(
            parent_widget=self.data_processing_widget_container,
            parent_class=self,
            root_class=self.root_class,
            label_text=RESULTS[result_id].title + f" [Data{result_id}]",
            result_id=result_id,
        )
        self.data_processing_objects[result_id] = data_processing_object
        self.data_processing_container_layout.addWidget(data_processing_object.widget)
        self.root_class.mark_dirty()

    def move_data_processing(self, result_id, delta):
        """Move a data-processing study up/down in the chain, re-order the cards to
        match, and recompute the processing chain (downstream inputs that became
        invalid are pruned automatically on reconfigure)."""
        if not DATA_MANAGER.move_in_chain(result_id, delta):
            return
        layout = self.data_processing_container_layout
        for chain_id in DATA_MANAGER.data_chain:
            obj = self.data_processing_objects.get(chain_id)
            if obj is not None:
                layout.removeWidget(obj.widget)
                layout.addWidget(obj.widget)
        # Reordering can invalidate explicit "DataN" references (a study could now point at a
        # step that follows it). Reset every study's source to "Auto" so the chain stays valid.
        for res in RESULTS.values():
            if hasattr(res.config, "data_source"):
                res.config.data_source = "Auto"
        self.recompute_all()

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
        self.root_class.mark_dirty()

    def _build_report_html(self) -> str:
        """One self-contained HTML document: each data-analysis result (in display order)
        with its tables and plots (plots are inline base64 PNGs, so the file is portable)."""
        from src.side_area_panel.modules.common.result.html_result import HTMLTableV2
        from src.side_area_panel.modules.common.result.plot_result import PlotV2

        parts = ["<html><body>"]
        for result_id in self.data_analysis_objects:
            result = RESULTS[result_id]
            parts.append(f"<h2>{result.title}</h2>")
            for element in result.result_elements:
                if isinstance(element, (HTMLTableV2, PlotV2)):
                    parts.append(element.get_html())
                parts.append("<br><br>")
            parts.append("<hr>")
        parts.append("</body></html>")
        return "".join(parts)

    def copy_all_results(self):
        """Copy every data-analysis result (in display order) to the clipboard as one HTML
        document -- the concatenation of each study's tables and plots."""
        from PySide6.QtCore import QMimeData
        from PySide6.QtGui import QGuiApplication

        mime_data = QMimeData()
        mime_data.setHtml(self._build_report_html())
        QGuiApplication.clipboard().setMimeData(mime_data)

    def export_report_html(self):
        """Save every data-analysis result as a single self-contained .html file (tables +
        inline plots), openable directly in Word or a browser."""
        import logging

        from PySide6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getSaveFileName(self.widget, "Export Report (HTML)", "", "HTML files (*.html)")
        if not file_path:
            return
        if not file_path.endswith(".html"):
            file_path += ".html"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self._build_report_html())
        except Exception as e:
            logging.error(f"Failed to export report to HTML: {e}")

    def move_data_analysis(self, result_id, delta):
        """Reorder an analysis card up/down. Analyses are leaves (not in the data chain), so
        this is purely the visual order in the analysis column."""
        ids = list(self.data_analysis_objects.keys())
        if result_id not in ids:
            return
        i = ids.index(result_id)
        j = i + delta
        if j < 0 or j >= len(ids):
            return
        ids[i], ids[j] = ids[j], ids[i]
        for rid in ids:
            widget = self.data_analysis_objects[rid].widget
            self.data_analysis_container_layout.removeWidget(widget)
            self.data_analysis_container_layout.addWidget(widget)
        self.data_analysis_objects = {rid: self.data_analysis_objects[rid] for rid in ids}
        self.root_class.mark_dirty()

    def duplicate_data_analysis(self, result_id):
        """Create an independent copy of an analysis study (same type + settings), compute it,
        and focus it."""
        import copy

        source = RESULTS[result_id]
        new_id = get_unique_result_id()
        RESULTS[new_id] = type(source)(
            unique_id=new_id,
            settings_panel_index=source.settings_panel_index,
            config=copy.deepcopy(source.config),
        )
        self.add_data_analysis(new_id)
        panel = self.root_class.settings_panel.panels[source.settings_panel_index]
        panel.configure(new_id)
        panel.recalculate()
        self.update_focus(new_id)

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

    def delete_result(self, result_id):
        self.root_class.action_activate_home_panel()
        self.remove_result(result_id)
        RESULTS.pop(result_id)
        DATA_MANAGER.try_to_remove_result(result_id)

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
        self.root_class.mark_dirty()
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
