#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#

import logging
from typing import TYPE_CHECKING, Union

import qtawesome as qta
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea, QVBoxLayout

from src.common.constant import DEBUG_LAYOUT
from src.common.decorators import log_method, log_method_noarg
from src.common.messages import Message, MessageType
from src.common.result.registry import RESULTS
from src.common.size import SettingsPanelSize
from src.common.ui_constructor import create_tool_button_qta
from src.common.unique_qss import set_stylesheet
from src.settings_panel.panels.registry import PanelRegistry

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
        self.tabledata = self.root_class.data_panel.tabledata
        self.widget = QtWidgets.QWidget(parent_widget)
        if DEBUG_LAYOUT:
            set_stylesheet(self.widget, "#id{border: 1px solid green; background-color: #efe;}")
        self.widget_layout = QVBoxLayout(self.widget)
        self.widget_layout.setContentsMargins(0, 0, 0, 0)
        self.widget_layout.setSpacing(0)
        self.widget.setLayout(self.widget_layout)

        self.study_widget = QtWidgets.QWidget(self.widget)
        self.study_widget.setFixedHeight(80)
        set_stylesheet(self.study_widget, "#id{border-bottom: 1px solid #ddd;}")

        self.widget_layout.addWidget(self.study_widget)

        self.recalculate_button = create_tool_button_qta(
            parent=self.widget,
            button_geometry=QtCore.QRect(10, 5, 50, 50),
            icon_path="ph.arrows-clockwise",
            icon_size=QtCore.QSize(40, 40),
        )
        self.auto_checkbox = QtWidgets.QCheckBox(self.study_widget)
        self.auto_checkbox.setText("Auto")
        self.auto_checkbox.setChecked(True)
        self.auto_checkbox.setGeometry(10, 60, 50, 20)
        self.recalculate_button.clicked.connect(self.recalculate)

        self.delete_button = create_tool_button_qta(
            parent=self.widget,
            button_geometry=QtCore.QRect((SettingsPanelSize.width - 50 - 10), 5, 50, 50),
            icon_path="mdi6.delete-outline",
            icon_size=QtCore.QSize(40, 40),
        )
        self.delete_button.clicked.connect(self.delete)

        self.copy_for_word_button = create_tool_button_qta(
            parent=self.widget,
            button_geometry=QtCore.QRect((SettingsPanelSize.width - 120), 5, 50, 50),
            icon_path="fa.file-word-o",
            icon_size=QtCore.QSize(40, 40),
        )
        self.copy_for_word_button.clicked.connect(self.copy_for_word)

        # Definition
        self.widget_for_elements = QtWidgets.QWidget()
        self.widget_for_elements.setFixedWidth(SettingsPanelSize.width)

        self.widget_for_elements_layout = QVBoxLayout(self.widget)
        self.widget_for_elements.setLayout(self.widget_for_elements_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        set_stylesheet(self.scroll_area, "#id{border: none;}")

        self.scroll_area.setWidget(self.widget_for_elements)

        self.widget_layout.addWidget(self.scroll_area)
        set_stylesheet(self.widget, "#id>QScrollBar{width: 15px;}")
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.elements = {}

    @log_method_noarg
    def is_auto_recalculate_enabled(self):
        if self.auto_checkbox is None:
            return False
        if self.auto_checkbox.isChecked():
            return True
        return False

    @log_method
    def setup(self, stretch=False):
        for element_id, element in self.elements.items():
            element.inject(parent_widget=self.widget_for_elements, handler=self.handler, element_id=element_id)
            element.setup()

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
        if self.recalculate_button is None:
            logging.error("No recalculate button")
            return

        if highlight:
            self.recalculate_button.setIcon(qta.icon("ph.arrows-clockwise", color="darkred"))
        else:
            self.recalculate_button.setIcon(qta.icon("ph.arrows-clockwise", color="black"))

    @log_method_noarg
    def recalculate(self):
        logging.warning("Recalculate handler not implemented")
        ...

    @log_method_noarg
    def delete(self):
        self.root_class.results_panel.display_none()
        self.root_class.result_selector_panel.delete_result(self.result_id)
        self.root_class.action_activate_data_panel()
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
        if message.message_type == MessageType.STATE_CHANGED:
            if self.configuring:
                return

            RESULTS[self.result_id].needs_update = True

            if self.is_auto_recalculate_enabled():
                self.recalculate()
            else:
                self.set_recalculate_button_highlight(True)
            self.root_class.result_selector_panel.refresh_result(result_id=self.result_id)
            return
        if message.message_type == MessageType.CLICKED:
            if message.caller_id == "compiled_filters":
                self.open_filter_handler()
                return
            if message.caller_id == "column_selector":
                self.open_column_selector_popup()
                return
        elif message.message_type == MessageType.FILTER_CLICKED:
            self.open_filter_handler()
            return
        logging.error(f"Handler not implemented for {message=}")

    def open_column_selector_popup(self):
        self.elements["column_selector"].configure_popup()
        PanelRegistry.COLUMN_SELECTOR.ui_instance.configure(
            caller_index=self.stacked_widget_index,
            finished_handler=self.popup_closed_handler,
            popup=self.elements["column_selector"].popup,
        )
        self.root_class.action_activate_panel_by_index(PanelRegistry.COLUMN_SELECTOR.settings_stacked_widget_index)

    def open_filter_handler(self):
        PanelRegistry.FILTER.ui_instance.configure(
            caller_index=self.stacked_widget_index,
            finished_handler=self.filter_closed_handler,
            filters=RESULTS[self.result_id].config.filters,
        )
        self.root_class.action_activate_panel_by_index(PanelRegistry.FILTER.settings_stacked_widget_index)

    def popup_closed_handler(self):
        self.elements["column_selector"].configure_from_popup()

    @log_method
    def filter_closed_handler(self, filters):
        RESULTS[self.result_id].config.filters = filters
        self.elements["compiled_filters"].configure(filters)
        self.handler(Message(message_type=MessageType.STATE_CHANGED, payload=None, caller_id="filter"))
