import logging

from PySide6 import QtWidgets
from PySide6.QtWidgets import QHBoxLayout, QTabWidget

from src.common.decorators import log_method, log_method_noarg
from src.common.ui_constructor import icon
from src.common.unique_qss import set_stylesheet
from src.data_panel.ui_data import DataPanelClass
from src.results_panel.ui_results import ResultsPanelClass
from src.settings_panel.ui_settings import SettingsPanelClass


class MainWindowClass(QtWidgets.QMainWindow):
    """
    Root class and root widget
    """

    def __init__(self):
        super().__init__()

        # Setup
        self.widget = self  # split class and widget for clarity
        self.setWindowTitle("StatPrism")

        # Definitions
        self.central_widget = QtWidgets.QWidget(self.widget)
        self.central_widget_layout = QHBoxLayout(self.central_widget)
        self.central_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.central_widget_layout.setSpacing(0)
        self.tab_widget = QTabWidget(self.central_widget)

        self.data_panel: DataPanelClass = DataPanelClass(
            parent_widget=self.tab_widget, parent_class=self.widget, root_class=self
        )
        self.results_panel: ResultsPanelClass = ResultsPanelClass(
            parent_widget=self.tab_widget, parent_class=self.widget, root_class=self
        )
        self.settings_panel: SettingsPanelClass = SettingsPanelClass(
            parent_widget=self.tab_widget, parent_class=self.widget, root_class=self
        )

        # Relations
        self.widget.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.central_widget_layout)
        self.central_widget_layout.addWidget(self.tab_widget)
        self.central_widget_layout.addWidget(self.settings_panel.widget)

        self.tab_widget.addTab(self.data_panel.widget, "Data")
        self.tab_widget.addTab(self.results_panel.widget, "Analysis")
        self.tab_widget.setTabPosition(QtWidgets.QTabWidget.TabPosition.West)
        self.tab_widget.tabBar().setDocumentMode(True)
        self.tab_widget.tabBar().setExpanding(True)

        # Misc
        self.setWindowIcon(icon(":/mat/resources/StatPrism_icon_small.ico"))
        set_stylesheet(
            self.tab_widget,
            """
        QTabWidget#id>QTabBar::tab:selected{
            background: #fff;
            font-size: 12pt;
            font-family: Segoe UI;
            font-weight: bold;
            width: 20px;
            border:none;
        }
        QTabWidget#id>QTabBar::tab:!selected {
            background: #eee;
            font-size: 12pt;
            font-family: Segoe UI;
            width: 20px;
            border:none;
        }
        """,
        )
        # Post-init
        self.tab_widget.setCurrentIndex(0)

        self.tab_widget.currentChanged.connect(self.on_tab_changed)

    @log_method
    def action_activate_column_panel(self, column_index):
        if (self.settings_panel.stacked_widget.currentIndex == self.settings_panel.column_panel_index) and (
            self.settings_panel.column_panel.column_index == column_index
        ):
            return
        logging.info("configuring column panel")
        self.settings_panel.stacked_widget.setCurrentIndex(self.settings_panel.column_panel_index)
        self.settings_panel.column_panel.configure(column_index)

    @log_method
    def action_current_column_begin_edit_title(self):
        self.settings_panel.column_panel.begin_edit_title()

    @log_method_noarg
    def action_activate_home_panel(self):
        self.settings_panel.stacked_widget.setCurrentIndex(self.settings_panel.home_panel_index)

    @log_method
    def action_activate_panel_by_index(self, index):
        if index is not None:
            self.settings_panel.stacked_widget.setCurrentIndex(index)

    @log_method
    def action_select_table_column(self, column_index):
        self.data_panel.tableview.selectColumn(column_index)

    @log_method
    def action_activate_columns_panel(self, column_indexes):
        if (self.settings_panel.stacked_widget.currentIndex == self.settings_panel.columns_panel_index) and (
            self.settings_panel.columns_panel.column_indexes == column_indexes
        ):
            return

        self.settings_panel.stacked_widget.setCurrentIndex(self.settings_panel.columns_panel_index)
        self.settings_panel.columns_panel.configure(column_indexes)

    @log_method_noarg
    def on_tab_changed(self):
        if len(self.results_panel.results) == 0:
            self.settings_panel.stacked_widget.setCurrentIndex(self.settings_panel.select_study_panel_index)
        # if self.tab_widget.currentIndex() == 1:
        #     self.settings_panel.stacked_widget.setCurrentIndex(self.settings_panel.select_study_panel_index)
        # else:
        #     self.settings_panel.stacked_widget.setCurrentIndex(self.settings_panel.home_panel_index)
