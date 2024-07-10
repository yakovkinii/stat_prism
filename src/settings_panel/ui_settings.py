from typing import TYPE_CHECKING

from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QMenuBar, QVBoxLayout

from src.common.constant import DEBUG_LAYOUT
from src.common.unique_qss import set_stylesheet
from src.settings_panel.panels.calculate import Calculate
from src.settings_panel.panels.column import Column
from src.settings_panel.panels.columns import Columns
from src.settings_panel.panels.correlation import Correlation
from src.settings_panel.panels.descriptive import Descriptive
from src.settings_panel.panels.home import Home
from src.settings_panel.panels.invert import Inverse
from src.settings_panel.panels.select_study import SelectStudy

if TYPE_CHECKING:
    from src.ui_main import MainWindowClass


class SettingsPanelClass:
    def __init__(self, parent_widget, parent_class, root_class):
        # Setup
        self.root_class: MainWindowClass = root_class
        self.parent_class: MainWindowClass = parent_class
        self.widget = QtWidgets.QWidget(parent_widget)
        if DEBUG_LAYOUT:
            set_stylesheet(self.widget, "#id{border: 1px solid red; background-color: #fee;}")
        self.widget_layout = QVBoxLayout(self.widget)
        self.widget_layout.setContentsMargins(0, 0, 0, 0)
        self.widget.setLayout(self.widget_layout)

        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred
        )
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

        # Todo move to module
        self.columns_panel_index = 3
        self.columns_panel: Columns = Columns(
            parent_widget=self.stacked_widget,
            parent_class=self,
            root_class=self.root_class,
            stacked_widget_index=self.columns_panel_index,
        )

        # Todo move to module
        self.select_study_panel_index = 4
        self.select_study_panel: SelectStudy = SelectStudy(
            parent_widget=self.stacked_widget,
            parent_class=self,
            root_class=self.root_class,
            stacked_widget_index=self.select_study_panel_index,
        )

        # Todo move to module
        self.calculate_panel_index = 5
        self.calculate_panel: Calculate = Calculate(
            parent_widget=self.stacked_widget,
            parent_class=self,
            root_class=self.root_class,
            stacked_widget_index=self.calculate_panel_index,
        )

        # Todo move to module
        self.descriptive_panel_index = 6
        self.descriptive_panel: Descriptive = Descriptive(
            parent_widget=self.stacked_widget,
            parent_class=self,
            root_class=self.root_class,
            stacked_widget_index=self.descriptive_panel_index,
        )

        self.correlation_panel_index = 7
        self.correlation_panel: Correlation = Correlation(
            parent_widget=self.stacked_widget,
            parent_class=self,
            root_class=self.root_class,
            stacked_widget_index=self.correlation_panel_index,
        )

        self.panels = [
            self.home_panel,
            self.column_panel,
            self.inverse_panel,
            self.columns_panel,
            self.select_study_panel,
            self.calculate_panel,
            self.descriptive_panel,
            self.correlation_panel,
        ]

        # Relations
        self.stacked_widget.addWidget(self.home_panel.widget)  # Todo move to module
        self.stacked_widget.addWidget(self.column_panel.widget)  # Todo move to module
        self.stacked_widget.addWidget(self.inverse_panel.widget)  # Todo move to module
        self.stacked_widget.addWidget(self.columns_panel.widget)  # Todo move to module
        self.stacked_widget.addWidget(self.select_study_panel.widget)  # Todo move to module
        self.stacked_widget.addWidget(self.calculate_panel.widget)  # Todo move to module
        self.stacked_widget.addWidget(self.descriptive_panel.widget)  # Todo move to module
        self.stacked_widget.addWidget(self.correlation_panel.widget)  # Todo move to module
        self.widget_layout.addWidget(self.stacked_widget)

        # Create a file menu and add actions
        menu_bar = QMenuBar(self.widget)
        self.widget_layout.setMenuBar(menu_bar)
        set_stylesheet(menu_bar, "#id{border-bottom: 1px solid #ddd; background-color: #eee;}")

        file_menu = QMenu("File", self.widget)
        help_menu = QMenu("Help", self.widget)
        open_action = QAction("Open", self.widget)
        save_action = QAction("Save project", self.widget)
        save_table_action = QAction("Export Table", self.widget)
        about_action = QAction("About", self.widget)

        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(help_menu)

        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(save_table_action)
        help_menu.addAction(about_action)

        # Post-init
        self.stacked_widget.setCurrentIndex(self.home_panel_index)

        open_action.triggered.connect(self.home_panel.open_handler)
        save_action.triggered.connect(self.home_panel.save_handler)
        save_table_action.triggered.connect(self.save_table_handler)
        about_action.triggered.connect(self.home_panel.about_handler)

    def save_table_handler(self):
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self.widget,
            "Save Table",
            "",
            "Excel Spreadsheet (*.xlsx);;",
        )
        if file_path:
            self.root_class.data_panel.tabledata.save_as_xlsx(file_path)
