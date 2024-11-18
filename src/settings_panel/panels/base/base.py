#
#  Copyright (c) 2024 Ivan I. Yakovkin. All rights reserved.
#

import logging
from typing import TYPE_CHECKING, Dict, Union

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea, QVBoxLayout

from src.common.decorators import log_method, log_method_noarg
from src.common.elements.base.base import BasePanelElement
from src.common.messages import Message
from src.common.registry import DEBTS, DebtType
from src.common.size import SettingsPanelSize
from src.common.ui_constructor import create_tool_button_qta
from src.common.unique_qss import set_stylesheet

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
        self.tabledata = self.root_class.data_panel.tabledata
        self.widget = QtWidgets.QWidget(parent_widget)

        self.widget_layout = QVBoxLayout(self.widget)
        self.widget_layout.setContentsMargins(0, 0, 0, 0)
        self.widget_layout.setSpacing(0)
        self.widget.setLayout(self.widget_layout)

        self.navigation_widget = QtWidgets.QWidget(self.widget)
        self.navigation_widget.setFixedHeight(80)
        set_stylesheet(self.navigation_widget, "#id{border-bottom: 1px solid #ddd;}")

        self.widget_layout.addWidget(self.navigation_widget)

        self.back_button = create_tool_button_qta(
            parent=self.widget,
            button_geometry=QtCore.QRect((SettingsPanelSize.width - 145 - 10), 10, 145, 60),
            icon_path="fa.remove",
            icon_size=QtCore.QSize(40, 40),
        )
        self.back_button.clicked.connect(self.back_button_pressed)

        self.ok_button = create_tool_button_qta(
            parent=self.widget,
            button_geometry=QtCore.QRect(10, 10, 145, 60),
            icon_path="fa.check",
            icon_size=QtCore.QSize(40, 40),
        )
        self.ok_button.clicked.connect(self.ok_button_pressed)

        # Definition
        self.widget_for_elements = QtWidgets.QWidget()
        # self.widget_for_elements.setFixedWidth(SettingsPanelSize.width)

        self.widget_for_elements_layout = QVBoxLayout(self.widget)
        self.widget_for_elements.setLayout(self.widget_for_elements_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        set_stylesheet(self.scroll_area, "#id{border: none;}")

        self.scroll_area.setWidget(self.widget_for_elements)
        self.scroll_area.setFixedWidth(SettingsPanelSize.width)

        self.widget_layout.addWidget(self.scroll_area)
        set_stylesheet(self.widget, "#id>QScrollBar{width: 15px;}")
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.elements: Dict[str, BasePanelElement] = {}

    @log_method
    def setup(self, stretch=False, navigation_elements=False, ok_button=False):
        if navigation_elements:
            self.navigation_widget.show()
        else:
            self.navigation_widget.hide()
        if ok_button:
            self.ok_button.show()
        else:
            self.ok_button.hide()

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
            for debt in DEBTS:
                if DebtType.ON_STUDY_CHANGE in debt.debt_type:
                    debt.resolve()

            self.root_class.action_activate_panel_by_index(self.caller_index)
        else:
            logging.error(f"Trying to activate caller {self.caller_index=}")

    @log_method_noarg
    def back_button_pressed(self):
        self.activate_caller()

    @log_method_noarg
    def ok_button_pressed(self):
        logging.warning("OK button pressed is not reimplemented in the subclass")
        self.activate_caller()

    @log_method
    def handler(self, message: Message):
        logging.error(f"Handler not implemented for {message=}")
