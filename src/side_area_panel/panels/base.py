#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import logging
from typing import TYPE_CHECKING, Dict, Union

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea, QVBoxLayout

from src.common.constant import SettingsPanelSize
from src.common.debt import DEBTS, DebtType
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
        # Setup
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

        self._cancel_button, _ = add_widget(
            widget=create_tool_button_qta(
                parent=self.widget,
                icon_path="mdi6.arrow-u-left-top",
                icon_size=QtCore.QSize(40, 40),
            ),
            outer_layout=self._navigation_widget_layout,
        )
        self._cancel_button.clicked.connect(self.back_button_pressed)

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

        # create_simple_tool_button_qta

        # self.back_button = create_tool_button_qta(
        #     parent=self.widget,
        #     button_geometry=QtCore.QRect(10, 10, 145, 60),
        #     icon_path="fa5s.arrow-left",
        #     icon_size=QtCore.QSize(40, 40),
        # )
        # self.back_button.clicked.connect(self.back_button_pressed)
        #
        # self.ok_button = create_tool_button_qta(
        #     parent=self.widget,
        #     button_geometry= QtCore.QRect((SettingsPanelSize.width - 145 - 10), 10, 145, 60),
        #
        #     icon_path="fa.check",
        #     icon_size=QtCore.QSize(40, 40),
        # )

        # Definition
        self.widget_for_elements = QtWidgets.QWidget()
        # self.widget_for_elements.setFixedWidth(SettingsPanelSize.width)

        self.widget_for_elements_layout = QVBoxLayout(self.widget)
        self.widget_for_elements.setLayout(self.widget_for_elements_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        set_stylesheet(self.scroll_area, css(border="none"))

        self.scroll_area.setWidget(self.widget_for_elements)
        self.scroll_area.setFixedWidth(SettingsPanelSize.width)

        self.widget_layout.addWidget(self.scroll_area)
        # set_stylesheet(self.widget, "#id>QScrollBar{width: 15px;}")
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
