#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import logging
from typing import TYPE_CHECKING, Union

import qtawesome as qta
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea, QVBoxLayout

from src.common.constant import SettingsPanelSize
from src.common.decorators import log_method, log_method_noarg
from src.common.messages import Message
from src.common.ui_constructor import create_tool_button_qta
from src.data.data_manager import DATA_MANAGER
from src.pyside_ext.elements.utility.layout_helpers import add_widget
from src.pyside_ext.layout import HBoxLayout
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.blueprint.registry import PanelRegistry
from src.side_area_panel.modules.common.result.registry import RESULTS

if TYPE_CHECKING:
    from src.ui_main import MainWindowClass


class BaseModulePanel:
    def __init__(
        self,
        parent_widget,
        parent_class,
        root_class,
        stacked_widget_index,
        stretch=True,
    ):
        # Setup
        self.study_index = None
        self.result_id: Union[int, None] = None
        self.configuring = True
        self.stretch = stretch
        self.stacked_widget_index = stacked_widget_index
        self.root_class: MainWindowClass = root_class
        self.parent_class = parent_class
        self.widget = QtWidgets.QWidget(parent_widget)

        self.widget_layout = QVBoxLayout(self.widget)
        self.widget_layout.setContentsMargins(0, 0, 0, 0)
        self.widget_layout.setSpacing(0)
        self.widget.setLayout(self.widget_layout)

        self._navigation_widget, self._navigation_widget_layout = add_widget(
            parent=self.widget,
            outer_layout=self.widget_layout,
            inner_layout_class=HBoxLayout,
            css=css(
                border_bottom=Style.General.border,
                border_color=Style.Color.BorderElevated,
            ),
        )
        self._navigation_widget_layout.setContentsMargins(10, 5, 10, 5)
        self._navigation_widget_layout.setSpacing(5)
        self._cancel_button, _ = add_widget(
            widget=create_tool_button_qta(
                parent=self.widget,
                icon_path="mdi6.arrow-u-left-top",
                icon_size=QtCore.QSize(40, 40),
            ),
            outer_layout=self._navigation_widget_layout,
        )
        self._cancel_button.clicked.connect(
            lambda: [
                self.root_class.main_area_panel.update_focus(None, None),
                self.root_class.action_activate_panel_by_index(PanelRegistry.HOME.settings_stacked_widget_index),
            ]
        )

        self.recalculate_button, _ = add_widget(
            widget=create_tool_button_qta(
                parent=self.widget,
                icon_path="ph.arrows-clockwise",
                icon_size=QtCore.QSize(40, 40),
            ),
            outer_layout=self._navigation_widget_layout,
        )
        self.recalculate_button.clicked.connect(self.recalculate)

        self.delete_button, _ = add_widget(
            widget=create_tool_button_qta(
                parent=self.widget,
                icon_path="mdi6.delete-outline",
                icon_size=QtCore.QSize(40, 40),
            ),
            outer_layout=self._navigation_widget_layout,
        )
        self.delete_button.clicked.connect(self.delete)

        self._navigation_widget_layout.addStretch()

        self._label, _ = add_widget(
            parent=self._navigation_widget,
            widget_class=QtWidgets.QLabel,
            outer_layout=self._navigation_widget_layout,
            css=css(
                font_size=Style.FontSize.larger,
                color=Style.Color.Text,
            ),
        )

        # Definition
        self.widget_for_elements = QtWidgets.QWidget()
        self.widget_for_elements.setFixedWidth(SettingsPanelSize.width)

        self.widget_for_elements_layout = QVBoxLayout(self.widget)
        self.widget_for_elements.setLayout(self.widget_for_elements_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        set_stylesheet(self.scroll_area, css(border="none"))

        self.scroll_area.setWidget(self.widget_for_elements)

        self.widget_layout.addWidget(self.scroll_area)
        set_stylesheet(self.widget, css("#id>QScrollBar", width=Style.General.scrollbar_width_css))
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.elements = {}  # Deprecated
        self.elements_: ItemInSidePanelWithAutoConfigHolder = ...  # to be renamed after deprecating self.elements
        self.main_function = ...

    @log_method
    def set_label(self, label: str):
        self._label.setText(label)
        self.delete_button.hide()
        self.recalculate_button.hide()

    def init_elements(self, elements_class):
        """Instantiate an iispwac Elements holder, lay it out, and wire its
        recalculate + filter-open handlers. New-pattern modules call this in setup_ui."""
        self.elements_ = elements_class().complete_init_of_items(
            parent_widget=self.widget_for_elements,
            parent_layout=self.widget_for_elements_layout,
            handler_on_recalculate=self.recalculate,
            stretch=True,
        )
        for item in self.elements_.iter_items():
            if hasattr(item, "set_handler_open_filter"):
                item.set_handler_open_filter(lambda it=item: self.open_filter_for(it))
        return self.elements_

    def open_filter_for(self, item):
        self._active_filter_item = item
        PanelRegistry.FILTER.ui_instance.configure(
            caller_index=self.stacked_widget_index,
            finished_handler=self.filter_closed_for,
            filters=item.filters,
        )
        self.root_class.action_activate_panel_by_index(PanelRegistry.FILTER.settings_stacked_widget_index)

    def filter_closed_for(self, filters):
        self._active_filter_item.set_filters(filters)
        self.recalculate()

    @log_method_noarg
    def is_auto_recalculate_enabled(self):
        return True
        # if self.auto_checkbox is None:
        #     return False
        # if self.auto_checkbox.isChecked():
        #     return True
        # return False

    @log_method
    def setup(self, stretch=False, label="BaseModulePanel"):
        for element_id, element in self.elements.items():
            try:
                element.inject(parent_widget=self.widget_for_elements, handler=self.handler, element_id=element_id)
            except Exception as e:
                logging.error(f"Error injecting element {element_id}: {e}")
                continue
            element.setup()

        self._label.setText(label)
        self.delete_button.hide()
        self.recalculate_button.hide()

        while self.widget_for_elements_layout.count():
            item = self.widget_for_elements_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for element in self.elements.values():
            self.widget_for_elements_layout.addWidget(element.widget)
        if stretch:
            self.widget_for_elements_layout.addStretch()

    @log_method
    def set_recalculate_button_highlight(self, highlight: bool):
        if highlight:
            self.recalculate_button.setIcon(qta.icon("ph.arrows-clockwise", color="darkred"))
        else:
            self.recalculate_button.setIcon(qta.icon("ph.arrows-clockwise", color="black"))

    @log_method
    def configure(self, result_id: int):
        self.configuring = True
        self.result_id = result_id
        self.elements_.configure(
            config=RESULTS[result_id].config,
            result_id=result_id,
        )
        # self.set_recalculate_button_highlight(RESULTS[result_id].needs_update)
        self.configuring = False

    @log_method_noarg
    def recalculate(self):
        if self.configuring:
            return
        result = RESULTS[self.result_id]
        result.config = result.config_class(**self.elements_.get_kwargs())
        self.elements_.clear_alerts()
        self.recalculate_on_done(self.main_function(elements=self.elements_, result=result))

    @log_method
    def recalculate_on_done(self, result):
        result.update_description()
        RESULTS[self.result_id] = result
        self.root_class.main_area_panel.refresh_result(result_id=self.result_id)
        # RESULTS[self.result_id].needs_update = False
        self.configure(result_id=self.result_id)

    @log_method_noarg
    def delete(self):
        self.root_class.main_area_panel.remove_result(self.result_id)
        DATA_MANAGER.remove_data_from_chain_if_exists(result_id=self.result_id)
        RESULTS.pop(self.result_id)

    @log_method_noarg
    def copy_for_word(self):
        self.root_class.results_panel.copy_for_word()

    @log_method_noarg
    def activate(self):
        if self.stacked_widget_index:
            self.root_class.action_activate_panel_by_index(self.stacked_widget_index)
        else:
            logging.error(f"{self.stacked_widget_index=}")

    @log_method
    def handler(self, message: Message):
        # Fallback handler. iispwac elements drive recalculation/filters directly
        # (see init_elements / open_filter_for); only legacy panels that still use
        # the self.elements dict (e.g. RawData) reach this, and they override it.
        logging.error(f"Handler not implemented for {message=}")
