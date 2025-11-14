#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import logging

from PySide6 import QtWidgets
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QStackedWidget, QWidget

from src.about import version
from src.common.decorators import log_method, log_method_noarg
from src.common.ui_constructor import icon
from src.main_area_panel.ui_main_area import MainAreaClass
from src.pyside_ext.elements.utility.layout_helpers import add_widget
from src.pyside_ext.layout import HBoxLayout, VBoxLayout
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.blueprint.registry import PanelRegistry
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

        self.stacked_widget = QStackedWidget(self.central_widget)
        self.main_area_panel: MainAreaClass = MainAreaClass(
            parent_widget=self.stacked_widget, parent_class=self.widget, root_class=self
        )
        self.stacked_widget.addWidget(self.main_area_panel.widget)

        self.main_area_display_widget, self.main_area_display_widget_layout = add_widget(
            parent=self.stacked_widget,
            inner_layout_class=VBoxLayout,
            # css=css(background_color=Style.Color.BackgroundElevated),
        )
        self.stacked_widget.addWidget(self.main_area_display_widget)

        self.settings_panel: SettingsPanelClass = SettingsPanelClass(
            parent_widget=self.central_widget, parent_class=self.widget, root_class=self
        )

        # Relations
        self.widget.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.central_widget_layout)
        self.central_widget_layout.addWidget(self.splitter)

        self.splitter.addWidget(self.stacked_widget)
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

    @log_method_noarg
    def activate_main_area_display(self):
        self.stacked_widget.setCurrentIndex(1)

    @log_method_noarg
    def activate_main_area_panel(self):
        self.stacked_widget.setCurrentIndex(0)

    @log_method_noarg
    def clean_up_main_area_display(self):
        for i in reversed(range(self.main_area_display_widget_layout.count())):
            widget_to_remove = self.main_area_display_widget_layout.itemAt(i).widget()
            if widget_to_remove is not None:
                self.main_area_display_widget_layout.removeWidget(widget_to_remove)
                widget_to_remove.deleteLater()
            else:
                self.main_area_display_widget_layout.removeItem(
                    self.main_area_display_widget_layout.itemAt(i)
                )

    @log_method
    def set_widget_in_main_area_display(self, widget: QWidget):
        self.clean_up_main_area_display()
        self.main_area_display_widget_layout.addWidget(widget)
        self.main_area_display_widget_layout.addStretch()

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
        self.settings_panel.stacked_widget.setCurrentIndex(PanelRegistry.HOME.settings_stacked_widget_index)

    @log_method
    def action_activate_panel_by_index(self, index):
        if index is not None:
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
