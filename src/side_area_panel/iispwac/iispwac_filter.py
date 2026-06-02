#  Copyright (c) 2023 StatPrism Team. All rights reserved.
from typing import List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from src.common.decorators import log_method_noarg
from src.pyside_ext.elements.filter import FilterSettings
from src.pyside_ext.elements.utility.layout_helpers import add_widget
from src.pyside_ext.elements.utility.primitive_elements import QWidgetClickable
from src.pyside_ext.layout import VBoxLayout
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfig


class IISPWACFilter(ItemInSidePanelWithAutoConfig):
    """Compiled-filter display for the iispwac pattern.

    Stores the active filters as its config value and, when clicked, asks the
    owning module panel to open the shared FILTER panel (wired in via
    ``set_handler_open_filter``). The panel calls ``set_filters`` with the result.
    """

    def __init__(self):
        super().__init__()
        self.filters: List[FilterSettings] = []
        self.filter_widgets = []
        self.handler_open_filter = None

    def post_init(self, name, parent_widget):
        self.name = name

        self.widget, self.layout = add_widget(
            parent=parent_widget,
            inner_layout_class=VBoxLayout,
            widget_class=QWidgetClickable,
        )
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.layout.setSpacing(4)
        self.widget.clicked.connect(self.on_clicked)

        self.label, _ = add_widget(
            widget=QLabel(self.widget),
            outer_layout=self.layout,
        )
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.filters_panel, self.filters_panel_layout = add_widget(
            parent=self.widget,
            inner_layout_class=VBoxLayout,
            outer_layout=self.layout,
        )
        self.filters_panel_layout.setContentsMargins(0, 0, 0, 0)
        self.filters_panel_layout.setSpacing(4)

        self._refresh()
        self.clear_alert()

    def _refresh(self):
        for filter_widget in self.filter_widgets:
            self.filters_panel_layout.removeWidget(filter_widget)
            filter_widget.deleteLater()
        self.filter_widgets = []

        if not self.filters:
            self.label.setText("No Active Filters")
            return

        self.label.setText("Active Filters:")
        for filter_settings in self.filters:
            filter_widget, _ = add_widget(
                parent=self.filters_panel,
                widget=QLabel(self.filters_panel),
                outer_layout=self.filters_panel_layout,
                css=css(
                    border=Style.General.border,
                    border_color=Style.Color.BorderElevated,
                ),
            )
            filter_widget.setText(filter_settings.get_text())
            filter_widget.setWordWrap(True)
            self.filter_widgets.append(filter_widget)

    def get_kwargs(self):
        return {self.name: list(self.filters)}

    def configure(self, **kwargs):
        filters = kwargs.get(self.name)
        self.filters = list(filters) if filters else []
        self._refresh()

    def set_filters(self, filters: List[FilterSettings]):
        self.filters = list(filters) if filters else []
        self._refresh()

    def on_clicked(self):
        if self.handler_open_filter is not None:
            self.handler_open_filter()

    def set_handler_open_filter(self, handler):
        self.handler_open_filter = handler

    @log_method_noarg
    def set_alert(self):
        set_stylesheet(self.widget, css(border="1px solid red"))

    @log_method_noarg
    def clear_alert(self):
        set_stylesheet(
            self.widget,
            css(border=Style.General.border, border_color=Style.Color.BorderElevated),
        )
