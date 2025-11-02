#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import logging

from PySide6 import QtWidgets
from PySide6.QtWebEngineWidgets import QWebEngineView

# from src._data_panel.ui_data import DataPanelClass
from src.about import version
from src.common.debt import DEBTS, DebtType
from src.common.decorators import log_method, log_method_noarg
from src.common.ui_constructor import icon
from src.main_area_panel.ui_main_area import MainAreaClass
from src.pyside_ext.layout import HBoxLayout
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.registry import PanelRegistry
from src.side_area_panel.ui_settings import SettingsPanelClass


class MainWindowClass(QtWidgets.QMainWindow):
    """
    Root class and root widget
    """

    def __init__(self):
        super().__init__()

        # Special
        self.current_file_path = None

        # Setup
        self.widget = self  # split class and widget for clarity
        self.setWindowTitle(f"StatPrism v{version}")

        # Definitions
        self.central_widget = QtWidgets.QWidget(self.widget)
        self.central_widget_layout = HBoxLayout(self.central_widget)

        self.splitter = QtWidgets.QSplitter(self.central_widget)
        # self.tab_widget = main_tab_widget(self.splitter)

        self.main_area_panel: MainAreaClass = MainAreaClass(
            parent_widget=self.central_widget, parent_class=self.widget, root_class=self
        )
        self.settings_panel: SettingsPanelClass = SettingsPanelClass(
            parent_widget=self.central_widget, parent_class=self.widget, root_class=self
        )

        # Relations
        self.widget.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.central_widget_layout)
        self.central_widget_layout.addWidget(self.splitter)

        self.splitter.addWidget(self.main_area_panel.widget)
        self.splitter.addWidget(self.settings_panel.widget)
        # increase size of splitter handle
        self.splitter.setHandleWidth(6)
        self.splitter.setSizes([1, 1])

        set_stylesheet(
            self.splitter,
            css(
                "#id::handle",
                background_color=Style.Color.BorderElevated,
            ),
        )

        # Misc
        self.setWindowIcon(icon(":/mat/resources/StatPrism_icon_small.ico"))

    def init_web_view_and_show_maximized(self, file_path=None):
        webview = QWebEngineView(self.central_widget)
        self.central_widget_layout.addWidget(webview)
        webview.setHtml("dummy")

        self.showMaximized()

        self.central_widget_layout.removeWidget(webview)
        webview.deleteLater()

        if file_path is not None:
            PanelRegistry.HOME.ui_instance.open_file(file_path)
            if file_path.endswith(".sp"):
                self.set_current_file_path(file_path)

    def set_current_file_path(self, file_path):
        self.current_file_path = file_path
        if file_path is None:
            self.setWindowTitle(f"StatPrism v{version}")
        else:
            self.setWindowTitle(f"StatPrism v{version}: {file_path}")

    @log_method
    def action_activate_column_panel(self, column_index):
        if (self.settings_panel.stacked_widget.currentIndex == PanelRegistry.COLUMN.settings_stacked_widget_index) and (
            PanelRegistry.COLUMN.ui_instance.column_index == column_index
        ):
            return
        logging.info("configuring column panel")
        self.settings_panel.stacked_widget.setCurrentIndex(PanelRegistry.COLUMN.settings_stacked_widget_index)
        PanelRegistry.COLUMN.ui_instance.configure(column_index)

    @log_method
    def action_current_column_begin_edit_title(self):
        PanelRegistry.COLUMN.ui_instance.begin_edit_title()

    @log_method_noarg
    def action_activate_home_panel(self):
        for debt in DEBTS:
            if debt.debt_type == DebtType.ON_STUDY_CHANGE:
                debt.resolve()

        self.settings_panel.stacked_widget.setCurrentIndex(PanelRegistry.HOME.settings_stacked_widget_index)

    @log_method
    def action_activate_panel_by_index(self, index):
        if index is not None:
            for debt in DEBTS:
                if debt.debt_type == DebtType.ON_STUDY_CHANGE:
                    debt.resolve()
            self.settings_panel.stacked_widget.setCurrentIndex(index)

    @log_method
    def action_activate_columns_panel(self, column_indexes):
        if (
            self.settings_panel.stacked_widget.currentIndex == PanelRegistry.COLUMNS.settings_stacked_widget_index
        ) and (PanelRegistry.COLUMNS.ui_instance.column_indexes == column_indexes):
            return

        self.settings_panel.stacked_widget.setCurrentIndex(PanelRegistry.COLUMNS.settings_stacked_widget_index)
        PanelRegistry.COLUMNS.ui_instance.configure(column_indexes)

    @log_method_noarg
    def action_activate_results_panel(self):
        logging.error("action_activate_results_panel is deprecated")
        # self.tab_widget.setCurrentIndex(1)

    @log_method_noarg
    def action_activate_data_panel(self):
        logging.error("action_activate_data_panel is deprecated")
        # self.tab_widget.setCurrentIndex(0)
