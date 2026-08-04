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
from typing import TYPE_CHECKING, Dict, Union

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea, QVBoxLayout

from src.common.constant import SettingsPanelSize
from src.common.decorators import log_method, log_method_noarg
from src.common.messages import Message
from src.common.ui_constructor import create_tool_button_qta
from src.pyside_ext.elements.base import BasePanelElement
from src.pyside_ext.elements.utility.layout_helpers import add_widget
from src.pyside_ext.layout import HBoxLayout
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.blueprint.registry import PanelRegistry

if TYPE_CHECKING:
    from src.ui_main import MainWindowClass


class BasePanel:
    def __init__(
        self,
        parent_widget,
        parent_class,
        root_class,
        stacked_widget_index,
    ):
        self.study_index = None
        self.result_id: Union[int, None] = None
        self.caller_index = None
        self.configuring = False
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

        self._ok_button, _ = add_widget(
            widget=create_tool_button_qta(
                parent=self.widget,
                icon_path="mdi6.check",
                icon_size=QtCore.QSize(40, 40),
            ),
            outer_layout=self._navigation_widget_layout,
        )
        self._ok_button.clicked.connect(self.ok_button_pressed)
        self._ok_button.setToolTip("OK")

        self._cancel_button, _ = add_widget(
            widget=create_tool_button_qta(
                parent=self.widget,
                icon_path="mdi6.arrow-u-left-top",
                icon_size=QtCore.QSize(40, 40),
            ),
            outer_layout=self._navigation_widget_layout,
        )
        self._cancel_button.clicked.connect(self.back_button_pressed)
        self._cancel_button.setToolTip("Back")

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

        self.widget_for_elements = QtWidgets.QWidget()

        self.widget_for_elements_layout = QVBoxLayout(self.widget)
        self.widget_for_elements.setLayout(self.widget_for_elements_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        set_stylesheet(self.scroll_area, css(border="none"))

        self.scroll_area.setWidget(self.widget_for_elements)
        self.scroll_area.setFixedWidth(SettingsPanelSize.width)

        self.widget_layout.addWidget(self.scroll_area)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.elements: Dict[str, BasePanelElement] = {}

    @log_method
    def setup(self, stretch=False, navigation_elements=True, ok_button=False, label="BasePanel"):
        if navigation_elements:
            self._navigation_widget.show()
        else:
            self._navigation_widget.hide()
        self._label.setText(label)
        if ok_button:
            self._ok_button.show()
        else:
            self._ok_button.hide()

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

    @log_method_noarg
    def activate_caller(self):
        if self.caller_index is not None:
            self.root_class.action_activate_panel_by_index(self.caller_index)
        else:
            logging.warning(f"Trying to activate caller {self.caller_index=}, activating home panel instead")
            self.root_class.main_area_panel.update_focus(None, None),
            self.root_class.action_activate_panel_by_index(PanelRegistry.HOME.settings_stacked_widget_index),

    @log_method_noarg
    def back_button_pressed(self):
        self.ok_button_pressed()

    @log_method_noarg
    def ok_button_pressed(self):
        logging.warning("OK button pressed is not reimplemented in the subclass")
        self.activate_caller()

    @log_method
    def handler(self, message: Message):
        logging.error(f"Handler not implemented for {message=}")
