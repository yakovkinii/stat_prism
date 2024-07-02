import logging
from typing import TYPE_CHECKING

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea, QVBoxLayout

from src.common.constant import DEBUG_LAYOUT
from src.common.decorators import log_method_noarg
from src.common.ui_constructor import create_tool_button_qta

if TYPE_CHECKING:
    from src.ui_main import MainWindowClass


class BaseSettingsPanel:
    def __init__(
        self,
        parent_widget,
        parent_class,
        root_class,
        stacked_widget_index,
        navigation_elements=False,
        ok_button=False,
    ):
        # Setup
        self.caller_index = None
        self.stacked_widget_index = stacked_widget_index
        self.root_class: MainWindowClass = root_class
        self.parent_class = parent_class
        self.tabledata = self.root_class.data_panel.tabledata
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
            self.navigation_widget.setStyleSheet("border-bottom: 1px solid #ddd;")

            self.widget_layout.addWidget(self.navigation_widget)

            self.back_button = create_tool_button_qta(
                parent=self.widget,
                button_geometry=QtCore.QRect((400 - 180), 10, 180, 60),
                icon_path="fa.remove",
                icon_size=QtCore.QSize(40, 40),
            )
            self.back_button.clicked.connect(self.back_button_pressed)

            if ok_button:
                self.ok_button = create_tool_button_qta(
                    parent=self.widget,
                    button_geometry=QtCore.QRect(10, 10, 180, 60),
                    icon_path="fa.check",
                    icon_size=QtCore.QSize(40, 40),
                )
                self.ok_button.clicked.connect(self.ok_button_pressed)

            # self.home_button = create_tool_button_qta(
            #     parent=self.widget,
            #     button_geometry=QtCore.QRect(400 - 120, 10, 120, 60),
            #     icon_path="fa.home",
            #     icon_size=QtCore.QSize(40, 40),
            # )
            # self.home_button.clicked.connect(self.root_class.action_activate_home_panel)

        # Definition
        self.widget_for_elements = QtWidgets.QWidget()
        self.widget_for_elements_layout = QVBoxLayout(self.widget)
        self.widget_for_elements.setLayout(self.widget_for_elements_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea{border: none;}")

        self.scroll_area.setWidget(self.widget_for_elements)

        self.widget_layout.addWidget(self.scroll_area)

        self.scroll_area.verticalScrollBar().setStyleSheet("width: 15px;")
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.elements = {}

    @log_method_noarg
    def place_elements(self):
        while self.widget_for_elements_layout.count():
            item = self.widget_for_elements_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for element in self.elements.values():
            self.widget_for_elements_layout.addWidget(element.widget)
        self.widget_for_elements_layout.addStretch()
        # current_height = 20
        # for element in self.elements.values():
        #     current_height = element.place(current_height)
        # self.widget_for_elements.setFixedHeight(current_height + 20)

    @log_method_noarg
    def activate(self):
        if self.stacked_widget_index:
            self.root_class.action_activate_panel_by_index(self.stacked_widget_index)
        else:
            logging.error(f"{self.stacked_widget_index=}")

    @log_method_noarg
    def activate_caller(self):
        if self.caller_index is not None:
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
