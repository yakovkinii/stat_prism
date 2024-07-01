from typing import TYPE_CHECKING

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QVBoxLayout

from core.globals.debug import DEBUG_LAYOUT
from core.globals.result import result_container
from core.module.settings.column.ui import Column
from core.module.settings.inverse.ui import Inverse
from core.registry.constants import NO_RESULT_SELECTED
from core.module.settings.home.ui import Home
from core.registry.utility import log_method_noarg


if TYPE_CHECKING:
    from core.panels.ui import MainWindowClass


class SettingsPanelClass:
    def __init__(self, parent_widget, parent_class, root_class):
        # Setup
        self.root_class: MainWindowClass = root_class
        self.parent_class: MainWindowClass = parent_class
        self.widget = QtWidgets.QWidget(parent_widget)
        if DEBUG_LAYOUT:
            self.widget.setStyleSheet("border: 1px solid red; background-color: #fee;")
        self.widget_layout = QVBoxLayout(self.widget)
        self.widget_layout.setContentsMargins(0, 0, 0, 0)
        self.widget.setLayout(self.widget_layout)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setMinimumSize(QtCore.QSize(410, 0))
        self.widget.setMaximumSize(QtCore.QSize(410, 16777215))

        # Definition
        self.stacked_widget = QtWidgets.QStackedWidget(self.widget)

        # Todo move to module
        self.home_panel_index = 0
        self.home_panel: Home = Home(
            parent_widget=self.stacked_widget,
            parent_class=self,
            root_class=self.root_class,
            stacked_widget_index=self.home_panel_index,
        )
        # Todo move to module
        self.column_panel_index = 1
        self.column_panel: Column = Column(
            parent_widget=self.stacked_widget,
            parent_class=self,
            root_class=self.root_class,
            stacked_widget_index=self.column_panel_index,
        )

        # Todo move to module
        self.inverse_panel_index = 2
        self.inverse_panel: Inverse = Inverse(
            parent_widget=self.stacked_widget,
            parent_class=self,
            root_class=self.root_class,
            stacked_widget_index=self.inverse_panel_index,
        )

        self.panels = [self.home_panel, self.column_panel, self.inverse_panel]

        # Relations
        self.stacked_widget.addWidget(self.home_panel.widget)  # Todo move to module
        self.stacked_widget.addWidget(self.column_panel.widget)  # Todo move to module
        self.stacked_widget.addWidget(self.inverse_panel.widget)  # Todo move to module
        self.widget_layout.addWidget(self.stacked_widget)

        # Post-init
        self.stacked_widget.setCurrentIndex(self.home_panel_index)

    @log_method_noarg
    def retranslateUI(self):
        for panel in self.panels:
            panel.retranslateUI()

    @log_method_noarg
    def update(self):
        result_id = result_container.current_result
        if result_id == NO_RESULT_SELECTED:
            self.stacked_widget.setCurrentIndex(0)
            return

        model_name = result_container.results[result_id].module_name
        self.stacked_widget.setCurrentIndex(self.registry[model_name].stacked_widget_index)

        if result_id != NO_RESULT_SELECTED:
            self.registry[model_name].setup_from_result_handler()
