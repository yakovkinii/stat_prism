import logging
from typing import TYPE_CHECKING

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QScrollArea
from core.globals.debug import DEBUG_LAYOUT
from core.registry.utility import log_method_noarg
from core.ui.common.common_ui import create_tool_button_qta

if TYPE_CHECKING:
    from core.ui.ui import MainWindowClass


class BaseSettingsPanel:
    def __init__(self, parent_widget, parent_class, root_class,
                 stacked_widget_index,navigation_elements=True,
                 ):
        # Setup
        self.caller_index = None
        self.stacked_widget_index = stacked_widget_index
        self.root_class: MainWindowClass = root_class
        self.parent_class = parent_class
        self.widget = QtWidgets.QWidget(parent_widget)
        if DEBUG_LAYOUT:
            self.widget.setStyleSheet("border: 1px solid green; background-color: #efe;")
        self.widget_layout = QVBoxLayout(self.widget)
        self.widget_layout.setContentsMargins(0, 0, 0, 0)
        self.widget_layout.setSpacing(0)
        self.widget.setLayout(self.widget_layout)

        # Navigation
        if navigation_elements:
            self.navigation_widget = QtWidgets.QWidget(self.widget)
            self.navigation_widget.setFixedHeight(80)
            self.widget_layout.addWidget(self.navigation_widget)

            self.back_button = create_tool_button_qta(
                parent=self.widget,
                button_geometry=QtCore.QRect(10, 10, 120, 60),
                icon_path="ri.arrow-go-back-fill",
                icon_size=QtCore.QSize(40, 40),
            )
            self.back_button.clicked.connect(self.back_button_pressed)
            # self.back_button.setEnabled(False)

            self.home_button = create_tool_button_qta(
                parent=self.widget,
                button_geometry=QtCore.QRect(400 - 120, 10, 120, 60),
                icon_path="fa.home",
                icon_size=QtCore.QSize(40, 40),
            )
            self.home_button.clicked.connect(self.root_class.action_activate_home_panel)



        # Definition
        self.widget_for_elements = QtWidgets.QWidget()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.scroll_area.setWidget(self.widget_for_elements)

        self.widget_layout.addWidget(self.scroll_area)

        self.scroll_area.verticalScrollBar().setStyleSheet("QScrollBar {width: 15px;}")
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.elements = {
        }

    @log_method_noarg
    def place_elements(self):
        current_height = 20
        for element in self.elements.values():
            current_height = element.place(current_height)
        self.widget_for_elements.setFixedHeight(current_height + 20)

    @log_method_noarg
    def retranslateUI(self):
        ...

    @log_method_noarg
    def activate(self):
        if self.stacked_widget_index:
            self.root_class.action_activate_panel_by_index(self.stacked_widget_index)
        else:
            logging.error(f'{self.stacked_widget_index=}')
    @log_method_noarg

    def back_button_pressed(self):
        self.root_class.action_activate_panel_by_index(self.caller_index)