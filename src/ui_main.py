import logging

from PySide6 import QtWidgets
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QHBoxLayout, QTabWidget

from src.common.decorators import log_method, log_method_noarg
from src.common.registry import DEBTS, DebtType
from src.common.ui_constructor import icon
from src.common.unique_qss import set_stylesheet
from src.data_panel.ui_data import DataPanelClass
from src.result_display_panel.ui_result_display import ResultDisplayClass
from src.result_selector_panel.ui_result_selector import ResultSelectorPanelClass
from src.settings_panel.panels.registry import PanelRegistry
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

        # dummy = QWebEngineView(self.central_widget)
        # dummy.setHtml('dummy')
        # self.central_widget_layout.addWidget(dummy)
        # dummy.showMaximized()

        # # Delete dummy
        # self.central_widget_layout.removeWidget(dummy)
        # dummy.deleteLater()

        self.splitter = QtWidgets.QSplitter(self.central_widget)
        self.tab_widget = QTabWidget(self.splitter)

        self.data_panel: DataPanelClass = DataPanelClass(
            parent_widget=self.tab_widget, parent_class=self.widget, root_class=self
        )
        self.results_panel: ResultDisplayClass = ResultDisplayClass(
            parent_widget=self.tab_widget, parent_class=self.widget, root_class=self
        )
        self.result_selector_panel: ResultSelectorPanelClass = ResultSelectorPanelClass(
            parent_widget=self.tab_widget, parent_class=self.widget, root_class=self
        )
        self.settings_panel: SettingsPanelClass = SettingsPanelClass(
            parent_widget=self.tab_widget, parent_class=self.widget, root_class=self
        )

        # Relations
        self.widget.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.central_widget_layout)
        self.central_widget_layout.addWidget(self.splitter)
        self.central_widget_layout.addWidget(self.settings_panel.widget)

        self.splitter.addWidget(self.tab_widget)
        self.splitter.addWidget(self.result_selector_panel.widget)
        # increase size of splitter handle
        self.splitter.setHandleWidth(6)
        # self.splitter.setSizes([1, 0])

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

    def init_web_view_and_show_maximized(self):
        webview = QWebEngineView(self.central_widget)
        self.central_widget_layout.addWidget(webview)
        webview.setHtml("dummy")

        self.showMaximized()

        self.central_widget_layout.removeWidget(webview)
        webview.deleteLater()

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
    def action_select_table_column(self, column_index):
        self.data_panel.tableview.selectColumn(column_index)

    @log_method
    def action_activate_columns_panel(self, column_indexes):
        if (
            self.settings_panel.stacked_widget.currentIndex == PanelRegistry.COLUMNS.settings_stacked_widget_index
        ) and (PanelRegistry.COLUMNS.ui_instance.column_indexes == column_indexes):
            return

        self.settings_panel.stacked_widget.setCurrentIndex(PanelRegistry.COLUMNS.settings_stacked_widget_index)
        PanelRegistry.COLUMNS.ui_instance.configure(column_indexes)

    @log_method_noarg
    def on_tab_changed(self):
        if self.tab_widget.currentIndex() == 1:
            self.splitter.setSizes([1, 1])

    @log_method_noarg
    def action_hide_result_selector(self):
        self.splitter.setSizes([1, 0])

    @log_method_noarg
    def action_activate_results_panel(self):
        self.tab_widget.setCurrentIndex(1)

    @log_method_noarg
    def action_activate_data_panel(self):
        self.tab_widget.setCurrentIndex(0)
