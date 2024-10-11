import logging
from typing import TYPE_CHECKING

from PySide6 import QtWidgets
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QMenuBar, QVBoxLayout

from src.common.size import SettingsPanelSize
from src.common.unique_qss import set_stylesheet
from src.modules.registry import ModuleRegistry, ModuleRegistryItem
from src.modules.registry_injector import inject_classes_to_module_registry
from src.settings_panel.panels.registry import PanelRegistry, PanelRegistryItem
from src.settings_panel.panels.registry_injector import inject_classes_to_panel_registry

if TYPE_CHECKING:
    from src.ui_main import MainWindowClass


class SettingsPanelClass:
    def __init__(self, parent_widget, parent_class, root_class):
        # Setup
        self.root_class: MainWindowClass = root_class
        self.parent_class: MainWindowClass = parent_class
        self.widget = QtWidgets.QWidget(parent_widget)

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
        self.widget.setFixedWidth(SettingsPanelSize.width)

        # Definition
        self.stacked_widget = QtWidgets.QStackedWidget(self.widget)

        self.max_used_panel_index = None

        self.panels = []

        self.widget_layout.addWidget(self.stacked_widget)

        # Create a file menu and add actions
        menu_bar = QMenuBar(self.widget)
        self.widget_layout.setMenuBar(menu_bar)
        set_stylesheet(menu_bar, "#id{border-bottom: 1px solid #ddd; background-color: #eee;}")

        file_menu = QMenu("File", self.widget)
        help_menu = QMenu("Help", self.widget)
        open_action = QAction("Open...", self.widget)
        save_action = QAction("Save", self.widget)
        save_as_action = QAction("Save As...", self.widget)
        save_table_action = QAction("Export Table...", self.widget)
        about_action = QAction("About", self.widget)

        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(help_menu)

        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)
        file_menu.addAction(save_table_action)
        help_menu.addAction(about_action)

        # Add all panels
        inject_classes_to_panel_registry()
        for panel in PanelRegistry:
            self.add_panel(panel.value)

        # Add all modules
        inject_classes_to_module_registry()
        for module in ModuleRegistry:
            self.add_module(module.value)

        # post-init
        self.stacked_widget.setCurrentIndex(PanelRegistry.HOME.value.settings_stacked_widget_index)

        open_action.triggered.connect(PanelRegistry.HOME.value.ui_instance.open_handler)
        save_action.triggered.connect(PanelRegistry.HOME.value.ui_instance.save_handler)
        save_as_action.triggered.connect(PanelRegistry.HOME.value.ui_instance.save_as_handler)
        save_table_action.triggered.connect(self.save_table_handler)
        about_action.triggered.connect(PanelRegistry.HOME.value.ui_instance.about_handler)

    def get_available_index(self):
        if self.max_used_panel_index is None:
            self.max_used_panel_index = 0
            return 0
        self.max_used_panel_index += 1
        return self.max_used_panel_index

    def add_module(self, panel_registry_item: ModuleRegistryItem):
        panel_registry_item.settings_stacked_widget_index = self.get_available_index()
        panel_registry_item.ui_instance = panel_registry_item.ui_class(
            parent_widget=self.stacked_widget,
            parent_class=self,
            root_class=self.root_class,
            stacked_widget_index=panel_registry_item.settings_stacked_widget_index,
        )
        panel_registry_item.ui_instance.setup_ui()
        self.panels.append(panel_registry_item.ui_instance)
        self.stacked_widget.addWidget(panel_registry_item.ui_instance.widget)

    def add_panel(self, panel_registry_item: PanelRegistryItem):
        panel_registry_item.settings_stacked_widget_index = self.get_available_index()
        panel_registry_item.ui_instance = panel_registry_item.ui_class(
            parent_widget=self.stacked_widget,
            parent_class=self,
            root_class=self.root_class,
            stacked_widget_index=panel_registry_item.settings_stacked_widget_index,
        )
        panel_registry_item.ui_instance.setup_ui()
        self.panels.append(panel_registry_item.ui_instance)
        self.stacked_widget.addWidget(panel_registry_item.ui_instance.widget)

    def save_table_handler(self):
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self.widget,
            "Save Table",
            "",
            "Excel Spreadsheet (*.xlsx);;",
        )
        if file_path:
            self.root_class.data_panel.tabledata.save_as_xlsx(file_path)


logging.debug("settings loaded")
