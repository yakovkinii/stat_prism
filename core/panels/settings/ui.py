import logging
from typing import TYPE_CHECKING

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QVBoxLayout, QMenuBar, QMenu, QAction

from core.globals.debug import DEBUG_LAYOUT
from core.globals.result import result_container
from core.module.settings.column.ui import Column
from core.module.settings.columns.ui import Columns
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





        # self.action_about.triggered.connect(self.about_handler)


        #
        #
        # self.widget_layout.setMenuBar(self.menu)
        # self.menu.addAction(self.menu_help.menuAction())
        # self.menu_help.addAction(self.action_about)
        # # self.action_about.triggered.connect(self.about_handler)


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

        self.columns_panel_index = 3
        self.columns_panel: Columns = Columns(
            parent_widget=self.stacked_widget,
            parent_class=self,
            root_class=self.root_class,
            stacked_widget_index=self.columns_panel_index,
        )

        self.panels = [self.home_panel, self.column_panel, self.inverse_panel, self.columns_panel]

        # Relations
        self.stacked_widget.addWidget(self.home_panel.widget)  # Todo move to module
        self.stacked_widget.addWidget(self.column_panel.widget)  # Todo move to module
        self.stacked_widget.addWidget(self.inverse_panel.widget)  # Todo move to module
        self.stacked_widget.addWidget(self.columns_panel.widget)  # Todo move to module
        self.widget_layout.addWidget(self.stacked_widget)

        # Create a file menu and add actions
        menu_bar = QMenuBar(self.widget)
        self.widget_layout.setMenuBar(menu_bar)
        menu_bar.setStyleSheet(
            "QMenuBar{"
               "border-bottom: 1px solid #ddd;"
               "background-color: #eee;"
            "}"
        )

        file_menu = QMenu("File", self.widget)
        help_menu = QMenu("Help", self.widget)
        open_action = QAction("Open", self.widget)
        save_action = QAction("Save", self.widget)
        about_action = QAction("About", self.widget)

        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(help_menu)

        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        help_menu.addAction(about_action)

        # Post-init
        self.stacked_widget.setCurrentIndex(self.home_panel_index)

        open_action.triggered.connect(self.home_panel.open_handler)
        save_action.triggered.connect(self.home_panel.save_handler)
        about_action.triggered.connect(self.home_panel.about_handler)

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
